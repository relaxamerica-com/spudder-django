import urllib, urllib2
import django
import settings
import json
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render
from spudmart.accounts.models import UserProfile
from spudmart.utils.url import get_return_url
from django.contrib.auth.models import User


def login(request):
    return render(request, 'accounts/login.html', {
        'client_id': settings.AMAZON_LOGIN_CLIENT_ID,
        'base_url': settings.SPUDMART_BASE_URL,
        'returnURL': get_return_url(request)
    })


def _handle_amazon_conn_error(request, json_data):
    return render(request, 'accounts/login.html', {
        'next': get_return_url(request),
        'error': json_data['error_description']
    })


def amazon_login(request):
    error = request.GET.get('error', None)
    return_url = get_return_url(request)

    if error is not None:
        error_message = request.GET.get('error_description') + '<br><a href="' + request.GET.get('error_uri') + '">Learn more</a>'
        return render(request, 'accounts/login.html', {
            'next': return_url,
            'error': error_message
        })

    access_token = request.GET.get('access_token')
    query_parameters = urllib.urlencode({'access_token': access_token})

    token_request = urllib2.urlopen('https://api.amazon.com/auth/O2/tokeninfo?%s' % query_parameters)
    json_data = json.load(token_request)
    if token_request.getcode() == 200:
        is_verified = json_data['aud'] == settings.AMAZON_LOGIN_CLIENT_ID
        if not is_verified:
            return render(request, 'accounts/login.html', {
                'next': return_url,
                'error': 'Verification failed! Please contact administrators'
            })

        profile_request = urllib2.urlopen('https://api.amazon.com/user/profile?%s' % query_parameters)
        profile_json_data = json.load(profile_request)
        if profile_request.getcode() == 200:
            amazon_user_id = profile_json_data['user_id']
            amazon_user_name = profile_json_data['name']

            user_not_exists = len(UserProfile.objects.filter(amazon_id=amazon_user_id)) == 0
            if user_not_exists:
                user = User.objects.create_user(amazon_user_name, profile_json_data['email'], amazon_user_id)
                user.save()

                user_profile = UserProfile(user=user)
                user_profile.amazon_id = amazon_user_id
                user_profile.amazon_access_token = access_token
                user_profile.save()

            user = authenticate(username=amazon_user_name, password=amazon_user_id)

            if not user_not_exists:
                profile = user.get_profile()
                profile.amazon_access_token = access_token
                profile.save()

            django.contrib.auth.login(request, user)

            return HttpResponseRedirect(return_url)
        else:
            return _handle_amazon_conn_error(request, profile_json_data)
    else:
        return _handle_amazon_conn_error(request, json_data)


def logout(request):
    return_url = get_return_url(request)
    django.contrib.auth.logout(request)

    return HttpResponseRedirect(return_url)