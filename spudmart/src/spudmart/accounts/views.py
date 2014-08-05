import os
import urllib, urllib2
import django
from django.core.exceptions import ObjectDoesNotExist
from django.utils.log import logger
import settings
import json
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, redirect
from spudderaccounts.utils import select_role_by_authentication_service, change_role_url, create_linked_authentication_service, get_authentication_wrapper
from spudderaccounts.wrappers import RoleBase
from spudderdomain.controllers import LinkedServiceController, RoleController
from spudmart.accounts.models import UserProfile
from spudmart.sponsors.models import SponsorPage
from spudmart.utils.url import get_return_url, get_request_param
from django.contrib.auth.models import User
from spudmart.accounts.utils import is_sponsor
import logging
from spudmart.CERN.rep import recruited_new_student, signed_up
from spudmart.CERN.models import Student, School
from spudderdomain.models import FanPage


def _accommodate_legacy_pre_V1_1_0_users(access_token, amazon_user_email, amazon_user_id):

    # Check if there is a UserProfile (old workflow) for this amazon id
    if not UserProfile.objects.filter(amazon_id=amazon_user_id):
        return

    # If there was a user profile then we need to convert and scrub the user
    UserProfile.objects.get(amazon_id=amazon_user_id).delete()

    try:
        # This is a legacy condition covering users that were created before V1.1.0
        user = User.objects.get(username=amazon_user_email)
        student = Student.objects.get(user=user).id

        role_controller = RoleController(user)
        user_role = role_controller.role_by_entity_type_and_entity_id(
            RoleController.ENTITY_STUDENT,
            student,
            RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_STUDENT))
        create_linked_authentication_service(
            user_role,
            LinkedServiceController.SERVICE_AMAZON,
            amazon_user_id,
            {
                'amazon_user_email': amazon_user_email,
                'amazon_user_id': amazon_user_id,
                'amazon_access_token': access_token
            })
    except ObjectDoesNotExist:
        # It is possible that previously accommodation went wrong and not all objects are currently available
        # If that situation occurs - just leave it as that, it should happen only for sponsors
        pass


def login(request):
    raise DeprecationWarning("This code is deprecated")
    return render(request, 'old/accounts/login.html', {
        'client_id': settings.AMAZON_LOGIN_CLIENT_ID,
        'base_url': settings.SPUDMART_BASE_URL,
        'returnURL': get_return_url(request)
    })


def _handle_amazon_conn_error(request, json_data):
    return render(request, 'old/accounts/login.html', {
        'next': get_return_url(request),
        'error': json_data['error_description']
    })


def create_student(user, school_id, referrer_id):
    """
    Creates a Student object to go with a new user.

    :param user: the User object linked to the Student
    :param school_id: the id of the School object
    :param referrer_id: a string containing the ID of the student who
        referred the new student
        equal to '' if no one referred new student
    """

    school = School.objects.get(id=school_id)
    student = Student(user=user, school=school)
    if school.num_students() == 0:
        student.isHead = True
    student.save()
    school.save()

    signed_up(student)

    # Referral points happen only after student has been saved to db,
    #  so put all referral stuff together
    if referrer_id:
        referrer = Student.objects.get(id=referrer_id)
        student.referred_by = referrer.user
        student.save()
        recruited_new_student(referrer, school)
    return student


def _process_amazon_login(access_token, amazon_user_email, amazon_user_id, request):

    # Check to see if we need to accomodate pre V1.1.0 accounts
    _accommodate_legacy_pre_V1_1_0_users(access_token, amazon_user_email, amazon_user_id)

    # Check to see if these credential are tied to a user role via an authentication service
    user_role = select_role_by_authentication_service(LinkedServiceController.SERVICE_AMAZON, amazon_user_id)

    # If there is a role then get the user, else get the currently authenticate user else create a new user
    if user_role and user_role.user:
        # Case - Amazon Login to existing account
        user = user_role.user

        # Get the role controller for this user
        role_controller = RoleController(user)
    else:
        # First get the user or create one
        if request.user.is_authenticated():
            # Case - Add new amazon login based role to existing account
            user = request.user

            # Make a note on the spudder users that as there are multiple roles a password needs to be set for this user
            user.spudder_user.mark_as_password_required()

        else:
            # Case - first time registration
            user = User.objects.create_user(amazon_user_email, amazon_user_email, amazon_user_id)
            user.save()

        # If there is a school id then this is a student registration
        school_id = request.GET.get('school_id', None)
        if school_id:
            # Create the student
            student = create_student(user, school_id, request.GET.get('referrer', None))

            # Get the Role controller for the current user
            role_controller = RoleController(user)

            # Get the user_role for this user/student combo
            user_role = role_controller.role_by_entity_type_and_entity_id(
                RoleController.ENTITY_STUDENT,
                student.id,
                RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_STUDENT))

            # Store the amazon linked authentication service details
            create_linked_authentication_service(
                user_role,
                LinkedServiceController.SERVICE_AMAZON,
                amazon_user_id,
                {
                    'amazon_user_email': amazon_user_email,
                    'amazon_user_id': amazon_user_id,
                    'amazon_access_token': access_token
                })

        # If the account_type is sponsor, create a SponsorPage
        account_type = get_request_param(request, 'account_type')
        if account_type == 'sponsor':
            # Create sponsor
            sponsor = SponsorPage(sponsor=user)
            sponsor.save()

            # Get the Role controller for the current user
            role_controller = RoleController(user)

            # Get the user_role for this user/student combo
            user_role = role_controller.role_by_entity_type_and_entity_id(
                RoleController.ENTITY_SPONSOR,
                sponsor.id,
                RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_SPONSOR))

            # Store the amazon linked authentication service details
            create_linked_authentication_service(
                user_role,
                LinkedServiceController.SERVICE_AMAZON,
                amazon_user_id,
                {
                    'amazon_user_email': amazon_user_email,
                    'amazon_user_id': amazon_user_id,
                    'amazon_access_token': access_token
                })
            
        # If the account_type is fan, create a FanPage
        if account_type == 'fan':
            # Create fan
            fan, _ = FanPage.objects.get_or_create(fan=user)
            fan.save()

            # Get the Role controller for the current user
            role_controller = RoleController(user)

            # Get the user_role for this user/student combo
            user_role = role_controller.role_by_entity_type_and_entity_id(
                RoleController.ENTITY_FAN,
                fan.id,
                RoleBase.RoleWrapperByEntityType(RoleController.ENTITY_FAN))

            # Store the amazon linked authentication service details
            create_linked_authentication_service(
                user_role,
                LinkedServiceController.SERVICE_AMAZON,
                amazon_user_id,
                {
                    'amazon_user_email': amazon_user_email,
                    'amazon_user_id': amazon_user_id,
                    'amazon_access_token': access_token
                })

    # Get and update the amazon auth record with the latest access token
    # Note that we don't use this at the moment but will in future - MG:20140708
    amazon_auth = get_authentication_wrapper(user_role, LinkedServiceController.SERVICE_AMAZON, amazon_user_id)
    amazon_auth.update_amazon_access_token(access_token)

    next_url = request.GET.get('next', None) or user_role.home_page_path
    if not request.user.is_authenticated():
        if user.spudder_user.has_set_password:
            return redirect('/users/account/signin/%s?next=%s' % (user.id, next_url))
        user = authenticate(
            username=user_role.user.username,
            password=amazon_auth.user_password)
        if user:
            django.contrib.auth.login(request, user)
        else:
            return Http404
    logging.info('%s?next=%s',change_role_url(user_role),next_url)
    return redirect('%s?next=%s' % (
        change_role_url(user_role),
        next_url))


def amazon_login(request):
    error = get_request_param(request, 'error', None)
    return_url = get_return_url(request)

    if error is not None:
        if error == 'access_denied':
            return HttpResponseRedirect('/accounts/amazon_required/')
        error_message = request.GET.get('error_description') + \
                        '<br><a href="' + request.GET.get('error_uri') + \
                        '">Learn more</a>'
        return render(request, 'old/accounts/login.html', {
            'next': return_url,
            'error': error_message
        })

    access_token = get_request_param(request, 'access_token')
    query_parameters = urllib.urlencode({'access_token': access_token})

    token_request = urllib2.urlopen('https://api.amazon.com/auth/O2/tokeninfo?%s' % query_parameters)
    json_data = json.load(token_request)
    if token_request.getcode() == 200:
        is_verified = json_data['aud'] == settings.AMAZON_LOGIN_CLIENT_ID
        if not is_verified:
            return render(request, 'old/accounts/login.html', {
                'next': return_url,
                'error': 'Verification failed! Please contact administrators'
            })

        profile_request = urllib2.urlopen('https://api.amazon.com/user/profile?%s' % query_parameters)
        profile_json_data = json.load(profile_request)

        if profile_request.getcode() == 200:

            # Extract the values we need from the Amazon profile
            amazon_user_id = profile_json_data['user_id']
            amazon_user_name = profile_json_data['name']
            amazon_user_email = profile_json_data['email']

            # Process the login as an amazon login, creating and adding roles to the user as needed
            return _process_amazon_login(access_token, amazon_user_email, amazon_user_id, request)

        else:
            return _handle_amazon_conn_error(request, profile_json_data)
    else:
        return _handle_amazon_conn_error(request, json_data)


def just_login(request):
    raise DeprecationWarning("This code is deprecated")
    error = get_request_param(request, 'error', None)

    if error is not None:
        error_message = request.GET.get('error_description') + \
                        '<br><a href="' + request.GET.get('error_uri') + \
                        '">Learn more</a>'
        return render(request, 'spuddercern/old/login.html', {
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
            return render(request, 'spuddercern/old/login.html', {
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
                if is_sponsor(user):
                    django.contrib.auth.login(request, user)

                    logging.info(request.user.is_authenticated())
                    logging.info(is_sponsor(request.user))

                    return HttpResponseRedirect('/dashboard/')
                else:
                    # Redirect to splash page w/o authentication
                    return HttpResponseRedirect('/cern/register')
            else:
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
    return render(request, 'spuddercern/pages/need_amazon_account.html')


def login_fake(request):
    # If we are not running locally then throw a 404
    if not bool(os.environ['SERVER_SOFTWARE'].startswith('Development')):
        raise Http404

    amazon_user_id = "somemadeupid1"
    amazon_user_name = "Test"
    amazon_user_email = "test@test.com"
    access_token = "someaccesstoken"
    
    fan_page, created = FanPage.objects.get_or_create(fan = request.user)
    if created:
        fan_page.save()

    return _process_amazon_login(access_token, amazon_user_email, amazon_user_id, request)


def sponsor_login(request):
    return render(request, 'spudderaccounts/pages/sponsor_login.html')


def fan_login(request):
    return render(request, 'spudderaccounts/pages/fan_login.html')
