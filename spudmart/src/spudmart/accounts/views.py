import urllib, urllib2
import django
from django.core.exceptions import ObjectDoesNotExist
import settings
import json
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from spudmart.accounts.models import UserProfile
from spudmart.utils.url import get_return_url, get_request_param
from django.contrib.auth.models import User
from spudmart.accounts.utils import is_sponsor, is_student
import logging
from spudmart.CERN.rep import recruited_new_student
from spudmart.CERN.models import Student, School


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


def create_student(user, school, referrer_id):
    """
    Creates a Student object to go with a new user.

    :param user: the User object linked to the Student
    :param school: the School the Student attends
    :param referrer_id: a string containing the ID of the student who
        referred the new student
        equal to '' if no one referred new student
    """

    student = Student(user=user, school=school)
    if school.num_students() == 0:
        student.isHead = True
    student.save()
    school.save()

    # Referral points happen only after student has been saved to db,
    #  so put all referral stuff together
    if referrer_id != '':
        referrer = Student.objects.get(id=referrer_id)
        student.referred_by = referrer.user
        student.save()
        recruited_new_student(referrer, school)


def amazon_login(request):
    error = get_request_param(request, 'error', None)
    return_url = get_return_url(request)

    if error is not None:
        if error == 'access_denied':
            return HttpResponseRedirect('/accounts/amazon_required/')
        error_message = request.GET.get('error_description') + \
                        '<br><a href="' + request.GET.get('error_uri') + \
                        '">Learn more</a>'
        return render(request, 'accounts/login.html', {
            'next': return_url,
            'error': error_message
        })

    access_token = get_request_param(request, 'access_token')
    query_parameters = urllib.urlencode({'access_token': access_token})

    token_request = urllib2.urlopen(
        'https://api.amazon.com/auth/O2/tokeninfo?%s' % query_parameters)
    json_data = json.load(token_request)
    if token_request.getcode() == 200:
        is_verified = json_data['aud'] == settings.AMAZON_LOGIN_CLIENT_ID
        if not is_verified:
            return render(request, 'accounts/login.html', {
                'next': return_url,
                'error': 'Verification failed! Please contact administrators'
            })

        profile_request = urllib2.urlopen(
            'https://api.amazon.com/user/profile?%s' % query_parameters)
        profile_json_data = json.load(profile_request)

        if profile_request.getcode() == 200:
            amazon_user_id = profile_json_data['user_id']
            amazon_user_name = profile_json_data['name']
            amazon_user_email = profile_json_data['email']

            profiles = UserProfile.objects.filter(amazon_id=amazon_user_id)
            if profiles.count() == 0:
                users_with_email = User.objects.filter(
                    email=amazon_user_email)

                if len(users_with_email) == 0:
                    user = User.objects.create_user(amazon_user_email,
                                                    amazon_user_email,
                                                    amazon_user_id)
                    user.save()
                else:  # User exists, but for some reason it's profile
                       #  wasn't created
                    user = users_with_email[0]

                user_profile = UserProfile(user=user)
                user_profile.amazon_id = amazon_user_id
                user_profile.amazon_access_token = access_token
                user_profile.username = amazon_user_name
                user_profile.save()

                # Scrub the request for data to create a student
                school_id = get_request_param(request, 'school_id')
                referrer = get_request_param(request, 'referrer')

                try:
                    sch = School.objects.get(id=school_id)
                except ObjectDoesNotExist:
                    pass
                except ValueError:
                    pass
                else:
                    create_student(user, sch, referrer)

            user = authenticate(username=amazon_user_email,
                                password=amazon_user_id)
            profile = user.get_profile()

            if not profile.amazon_access_token:
                profile.amazon_access_token = access_token
                profile.save()

            django.contrib.auth.login(request, user)
            
            has_next_in_url = (return_url != '/')
            
            logging.info(has_next_in_url)
            logging.info(request.user.is_authenticated())
            logging.info(is_sponsor(request.user))
            
            if request.user.is_authenticated() and not has_next_in_url:
                if is_sponsor(request.user):
                    return_url = '/dashboard'
                elif is_student(request.user):
                    return_url = '/cern/'

            return HttpResponseRedirect(return_url)
        else:
            return _handle_amazon_conn_error(request, profile_json_data)
    else:
        return _handle_amazon_conn_error(request, json_data)


def just_login(request):
    error = get_request_param(request, 'error', None)

    if error is not None:
        error_message = request.GET.get('error_description') + \
                        '<br><a href="' + request.GET.get('error_uri') + \
                        '">Learn more</a>'
        return render(request, 'cern/login.html', {
            'error': error_message
        })

    access_token = get_request_param(request, 'access_token')
    query_parameters = urllib.urlencode({'access_token': access_token})

    token_request = urllib2.urlopen(
        'https://api.amazon.com/auth/O2/tokeninfo?%s' % query_parameters)
    json_data = json.load(token_request)
    if token_request.getcode() == 200:
        is_verified = json_data['aud'] == settings.AMAZON_LOGIN_CLIENT_ID
        if not is_verified:
            return render(request, 'cern/login.html', {
                'error': 'Verification failed! Please contact administrators'
            })

        profile_request = urllib2.urlopen(
            'https://api.amazon.com/user/profile?%s' % query_parameters)
        profile_json_data = json.load(profile_request)

        if profile_request.getcode() == 200:
            amazon_user_id = profile_json_data['user_id']
            amazon_user_name = profile_json_data['name']
            amazon_user_email = profile_json_data['email']

            profiles = UserProfile.objects.filter(amazon_id=amazon_user_id)
            if profiles.count() == 0:
                users_with_email = User.objects.filter(
                    email=amazon_user_email)

                if len(users_with_email) == 0:
                    return HttpResponseRedirect('/cern/')
                else:  # User exists, but for some reason it's profile
                    # wasn't created
                    user = users_with_email[0]

                user_profile = UserProfile(user=user)
                user_profile.amazon_id = amazon_user_id
                user_profile.amazon_access_token = access_token
                user_profile.username = amazon_user_name
                user_profile.save()

            user = authenticate(username=amazon_user_email,
                                password=amazon_user_id)
            profile = user.get_profile()

            if not profile.amazon_access_token:
                profile.amazon_access_token = access_token
                profile.save()

            try:
                Student.objects.get(user=user)
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/cern/register')

            django.contrib.auth.login(request, user)

            logging.info(request.user.is_authenticated())
            logging.info(is_sponsor(request.user))

            return HttpResponseRedirect('/cern/')
        else:
            return _handle_amazon_conn_error(request, profile_json_data)
    else:
        return _handle_amazon_conn_error(request, json_data)


def logout(request):
    return_url = get_return_url(request)
    django.contrib.auth.logout(request)

    return HttpResponseRedirect(return_url)


def fix_accounts(request):
    users = User.objects.all()

    for user in users:
        try:
            profile = user.get_profile()
            profile.username = user.username
            profile.save()

            user.username = user.email
            user.save()
        except ObjectDoesNotExist:
            pass

    return HttpResponse('Done...')


def amazon_required(request):
    """
    Displays a clear error page when user does not share info w/Spudder

    :param request: request to render error page
    :return: Simple error page explaining that Spudder/CERN requires
        the user to share information from Amazon
    """
    return render(request, 'CERN/need-amazon-account.html')