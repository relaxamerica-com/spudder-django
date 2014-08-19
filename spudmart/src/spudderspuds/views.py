import re
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
import simplejson
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderaccounts.utils import change_current_role
from spudderdomain.controllers import TeamsController, RoleController, SpudsController
from spudderdomain.models import FanPage
from spudderkrowdio.utils import stop_following, start_following
from spuddersocialengine.models import SpudFromSocialMedia
from spudderspuds.forms import FanSigninForm, FanRegisterForm, FanPageForm, FanPageSocialMediaForm
from spudderspuds.utils import create_and_activate_fan_role, is_signin_claiming_spud
from spudmart.upload.models import UploadedFile
from spudmart.utils.cover_image import reset_cover_image, save_cover_image_from_request


def landing_page(request):
    return render(request, 'spudderspuds/pages/landing_page.html')


def fan_signin(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return redirect('/spuds')
    template_data = {}
    if request.method == "POST":
        form = FanSigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            fan = FanPage.objects.filter(fan=user)[0]
            change_current_role(request, RoleController.ENTITY_FAN, fan.id)
            is_signin_claiming_spud(
                request,
                fan,
                form.cleaned_data.get('twitter', None),
                form.cleaned_data.get('spud_id', None))
            return redirect('/spuds')
    else:
        form = FanSigninForm(initial=request.GET)
    template_data["form"] = form
    return render_to_response(
        'spudderspuds/pages/user_signin.html',
        template_data,
        context_instance=RequestContext(request))


def fan_register(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return redirect('/spuds')
    if request.current_role and not is_fan(request.current_role) and not user_has_fan_role(request):
        if request.GET.get('twitter', None) and request.GET.get('spud_id', None):
            return redirect(
                '/spuds/register_add_fan_role?twitter=%s&spud_id=%s' %
                (request.GET['twitter'], request.GET['spud_id']))
        else:
            return redirect('/spuds/register_add_fan_role')
    template_data = {}
    if request.method == "POST":
        form = FanRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username, username, password)
            user.save()
            user.spudder_user.mark_password_as_done()
            fan_role = create_and_activate_fan_role(request, user)
            login(request, authenticate(username=username, password=password))
            is_signin_claiming_spud(
                request,
                fan_role.entity,
                form.cleaned_data.get('twitter', None),
                form.cleaned_data.get('spud_id', None))
            return redirect('/fan/%s/edit?new_registration=true' % fan_role.entity.id)
    else:
        form = FanRegisterForm(initial=request.GET)
    template_data["form"] = form
    return render_to_response(
        'spudderspuds/pages/user_register.html',
        template_data,
        context_instance=RequestContext(request))


def user_add_fan_role(request):
    if not request.current_role:
        return redirect('/spuds/register')
    fan_role = create_and_activate_fan_role(request, request.user)
    return redirect('/fan/%s/edit?new_registration=true' % fan_role.entity.id)


def fan_profile_view(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    entity_id = None
    if request.current_role:
        entity_id = request.current_role.entity.id
    return render(request, 'spudderspuds/fans/pages/fan_page_view.html', {
        'page': page,
        'fan_spuds': SpudsController.GetSpudsForFan(page),
        'can_edit': entity_id == page.id
    })


def fan_profile_edit(request, page_id):
    fan_page = get_object_or_404(FanPage, pk=page_id)
    profile_form = FanPageForm(initial=fan_page.__dict__)
    social_accounts_form = FanPageSocialMediaForm(initial=fan_page.__dict__)
    if request.method == 'POST':
        profile_form = FanPageForm(request.POST)
        social_accounts_form = FanPageSocialMediaForm(request.POST)
        if profile_form.is_valid() and social_accounts_form.is_valid():
            for attr in ('name', 'date_of_birth', ):
                fan_page.__setattr__(attr, profile_form.cleaned_data[attr])
            for attr in ('twitter', 'facebook', 'google_plus', 'instagram', ):
                fan_page.__setattr__(attr, social_accounts_form.cleaned_data.get(attr, ''))
            fan_page.save()
        return redirect('/fan/%s' % fan_page.id)
    return render(request, 'spudderspuds/fans/pages/fan_page_edit.html', {
        'profile_form': profile_form,
        'social_accounts_form': social_accounts_form,
        # 'page': page,
        'new_registration': request.GET.get('new_registration', False)
    })


def fan_profile_save_avatar(request, page_id):
    avatar_id = request.POST['avatar'].split('/')[3]
    avatar = get_object_or_404(UploadedFile, pk=avatar_id)

    page = get_object_or_404(FanPage, pk=page_id)
    page.avatar = avatar
    page.save()

    return HttpResponse('ok')


def fan_profile_edit_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)

    return render(request, 'components/coverimage/edit_cover_image.html', {
        'name': 'Fan Page',
        'return_url': "/fan/%s" % page.id,
        'post_url': '/fan/%s/save_cover' % page.id,
        'reset_url': '/fan/%s/reset_cover' % page.id
    })


def fan_profile_reset_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    reset_cover_image(page)

    return HttpResponse('OK')


def fan_profile_save_cover(request, page_id):
    page = get_object_or_404(FanPage, pk=page_id)
    save_cover_image_from_request(page, request)

    return HttpResponse()


def fan_my_teams(request, page_id):
    template_data = {
        'teams': TeamsController.TeamsAdministeredByRole(request.current_role),
        'role_dashboard': 'spudderspuds/base.html',
        'additional_nav': render_to_string(
            'spudderspuds/components/main_nav.html',
            {'active': 'teams'},
            context_instance=RequestContext(request))}
    return render(request, 'components/sharedpages/teams/teams_list.html', template_data)


def claim_atpostspud(request, spud_id):
    try:
        spud = SpudFromSocialMedia.objects.get(id=spud_id)
    except SpudFromSocialMedia.DoesNotExist:
        spud = None
    template_data = {
        'spud': spud.expanded_data if spud else None,
        'spud_id': spud.id if spud else None
    }
    if request.method == "POST":
        action = request.POST.get('action', None)
        if action == "change_twitter" or action == "set_twitter":
            new_username = spud.expanded_data['user']['username']
            fan = request.current_role.entity
            fan.twitter = new_username
            fan.save()
            controller = SpudsController(request.current_role)
            controller.add_spud_from_fan(spud)
            template_data['username_changed'] = action == "change_twitter"
            template_data['username_set'] = action == "set_twitter"
    return render_to_response(
        'spudderspuds/pages/claim_atpostspud.html',
        template_data,
        context_instance=RequestContext(request))


def start_following_view(request):
    """
    Current role (fan) starts following entity in request
    :param request: a POST request
    :return: the response from the KrowdIO API on success,
        or an HttpResponseNotAllowed response
    """
    if request.method == 'POST':
        origin = str(request.POST.get('origin', ''))
        entity_id = entity_type = None
        if re.match(r'/venues/view/\d+', origin):
            entity_type = 'Venue'
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+', origin):
            entity_type = 'fan'
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/page/\d+', origin):
            entity_type = 'Team'
            entity_id = str.split(origin, '/')[-1]

        json = start_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def stop_following_view(request):
    """
    Current role (fan) stopsfollowing entity in request
    :param request: a POST request
    :return: the response from the KrowdIO API on success,
        or an HttpResponseNotAllowed response
    """
    if request.method == 'POST':
        origin = str(request.POST.get('origin', ''))
        entity_id = entity_type = None
        if re.match(r'/venues/view/\d+', origin):
            entity_type = 'Venue'
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+', origin):
            entity_type = 'fan'
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/page/\d+', origin):
            entity_type = 'Team'
            entity_id = str.split(origin, '/')[-1]

        json = stop_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])
