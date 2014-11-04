from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseNotFound, HttpResponseRedirect
import settings
from uuid import uuid4
from spudderaccounts.forms import ProfileDetailsForm, CreatePasswordForm, SigninForm, ForgotPasswordForm, \
    ResetPasswordForm
from spudderaccounts.models import Invitation, Notification
from spudderaccounts.utils import select_all_user_roles, change_current_role, select_most_appropriate_user_role
from spudderdomain.controllers import RoleController, CommunicationController
from spudderaccounts.wrappers import RoleBase


def accounts_signin(request, user_id):
    signin_form = SigninForm(initial={'user_id': user_id, 'next_url': request.GET.get('next', '/cern')})
    if request.method == 'POST':
        signin_form = SigninForm(request.POST)
        if signin_form.is_valid():
            password = signin_form.cleaned_data.get('password')
            user = authenticate(
                username=User.objects.get(id=signin_form.cleaned_data.get('user_id')).username,
                password=password)
            login(request, user)
            return redirect(signin_form.cleaned_data.get('next_url'))
    return render_to_response(
        'spudderaccounts/pages/signin_with_password.html',
        {'signin_form': signin_form},
        context_instance=RequestContext(request))


@login_required(login_url='/accounts/signin')
def accounts_dashboard(request):
    role_controller = RoleController(request.user)
    user_roles = select_all_user_roles(role_controller)
    template_data = {
        'roles': user_roles
    }
    profile_details_form = ProfileDetailsForm(
        initial={'first_name': request.user.first_name, 'last_name': request.user.last_name})
    if request.method == "POST":
        if request.POST.get('form', None) == "profile_detail":
            profile_details_form = ProfileDetailsForm(request.POST)
            if profile_details_form.is_valid():
                request.user.first_name = profile_details_form.cleaned_data.get('first_name', "")
                request.user.last_name = profile_details_form.cleaned_data.get('last_name', "")
                request.user.save()
                template_data['profile_details_form_saved'] = True
    template_data['profile_details_form'] = profile_details_form
    return render_to_response(
        'spudderaccounts/pages/dashboard.html',
        template_data,
        context_instance=RequestContext(request))


@login_required(login_url='/accounts/signin')
def accounts_manage_role(request, entity_type, entity_id):
    role_controller = RoleController(request.user)
    if entity_type == RoleController.ENTITY_STUDENT:
        role = role_controller.role_by_entity_type_and_entity_id(
            entity_type,
            entity_id,
            RoleBase.RoleWrapperByEntityType(entity_type))
        if not role:
            messages.add_message(request, messages.ERROR, "There was an error loading that role.")
            return redirect('/users')
        if not role.user_is_owner(request.user):
            messages.add_message(request, messages.WARNING, "You are not the owner of that role.")
            return redirect('/users')
    return render_to_response(
        'spudderaccounts/pages/role_manage.html',
        {'role': role},
        context_instance=RequestContext(request))


def accounts_delete_role(request, entity_type, entity_id):
    pass


def accounts_activate_role(request, entity_type, entity_id):
    role = RoleController.GetRoleForEntityTypeAndID(
        entity_type,
        entity_id,
        RoleBase.RoleWrapperByEntityType(entity_type))
    change_current_role(request, entity_type, entity_id)

    next_url = request.GET.get('next', None)
    if next_url is None:
        next_url = role.home_page_path
    return redirect(next_url or '/users')


def accounts_add_role(request):
    return render_to_response(
        'spudderaccounts/pages/add_new_role.html',
        {},
        context_instance=RequestContext(request))


def accounts_create_role(request, entity_type):
    pass  # TODO: working here MG: 20140704


def accounts_create_password(request):
    password_form = CreatePasswordForm(initial={'next_url': request.GET.get('next', request.current_role.home_page_path if request.current_role else '/')})
    if request.method == 'POST':
        password_form = CreatePasswordForm(request.POST)
        if password_form.is_valid():
            user = request.user
            user.set_password(password_form.cleaned_data.get('password_1'))
            user.save()
            user.spudder_user.mark_password_as_done()
            messages.success(request, "Your new password was saved!")
            return redirect(password_form.cleaned_data.get('next_url'))
    return render_to_response(
        'spudderaccounts/pages/create_password.html',
        {'password_form': password_form},
        context_instance=RequestContext(request))


def accounts_signin_choose_account(request):
    if request.user.is_authenticated():
        logout(request)
    return render_to_response('spudderaccounts/pages/signin_choose_account.html', {
        'AMAZON_CLIENT_ID': settings.AMAZON_LOGIN_CLIENT_ID,
        'base_url': settings.SPUDMART_BASE_URL,
    })


def account_forgot_password(request):
    if request.user.is_authenticated():
        logout(request)

    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            role_controller = RoleController(user)
            role = select_most_appropriate_user_role(role_controller)

            notification, created = Notification.objects.get_or_create(
                notification_type=Notification.RESET_PASSWORD,
                target_entity_id=role.entity.id,
                target_entity_type=role.entity_type
            )
            token = str(uuid4())
            link = '%s/users/account/reset_password?token=%s' % (settings.SPUDMART_BASE_URL, token)
            notification.extras = {'link': link, 'token': token}
            notification.save()
            CommunicationController.CommunicateWithEmail([email], **{'notification': notification})

            return render_to_response('spudderaccounts/pages/reset_password_link_sent.html', {'email': email})
    data = {'form': form}
    return render_to_response('spudderaccounts/pages/forgot_password.html', data)


def account_reset_password(request):
    if request.method == 'GET':
        password_form = ResetPasswordForm(initial=request.GET)
        if not password_form.is_valid_token():
            return HttpResponseNotFound()

    if request.method == 'POST':
        password_form = ResetPasswordForm(request.POST)
        if not password_form.is_valid_token():
            return HttpResponseNotFound()
        if password_form.is_valid():
            role = RoleController.GetRoleForEntityTypeAndID(
                password_form.notification.target_entity_type, password_form.notification.target_entity_id,
                RoleBase.RoleWrapperByEntityType(password_form.notification.target_entity_type)
            )
            user = role.user
            user.set_password(password_form.cleaned_data.get('password_1'))
            user.save()
            user.spudder_user.mark_password_as_done()
            messages.success(request, "Your new password was saved!")
            # remove notification
            password_form.notification.delete()
            return redirect('/challenges/signin')
    return render_to_response(
        'spudderaccounts/pages/create_password.html',
        {
            'password_form': password_form,
            'reset_password': True
        },
        context_instance=RequestContext(request))


def accept_invitation(request, invitation_id):
    try:
        invitation = Invitation.objects.get(id=invitation_id, status=Invitation.PENDING_STATUS)
        if invitation.invitation_type == Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION:
            request.session['invitation_id'] = invitation_id
            return HttpResponseRedirect('/spuds/register?email_address=%s' % invitation.invitee_entity_id)
        else:
            raise Invitation.DoesNotExist()
    except Invitation.DoesNotExist:
        return HttpResponseNotFound()


def cancel_invitation(request, invitation_id):
    try:
        invitation = Invitation.objects.get(id=invitation_id, status=Invitation.PENDING_STATUS)
        if not invitation.invitation_type == Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION:
            raise Invitation.DoesNotExist()
    except Invitation.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'GET':
        return render(request, 'spudderaccounts/pages/cancel_invitation.html', {
            'entity_name': invitation.invitee_entity_id
        })
    if request.method == 'POST':
        invitation.status = Invitation.REVOKED_STATUS
        invitation.save()
        return HttpResponseRedirect('/team/%s/admins' % invitation.target_entity_id)
