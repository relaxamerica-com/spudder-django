import re
from random import shuffle
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
import simplejson
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleFan
from spudderdomain.controllers import TeamsController, RoleController, SpudsController, EntityController
from spudderdomain.models import FanPage, TeamPage, TeamAdministrator
from spudderkrowdio.models import FanFollowingEntityTag, KrowdIOStorage
from spuddersocialengine.models import SpudFromSocialMedia
from spudderspuds.forms import FanSigninForm, FanRegisterForm, FanPageForm, FanPageSocialMediaForm
from spudderspuds.utils import create_and_activate_fan_role, is_signin_claiming_spud
from spudmart.CERN.models import Student
from spudmart.CERN.rep import team_gained_follower, team_tagged_in_spud
from spudmart.accounts.templatetags.accounts import fan_page_name, user_name
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.models import UploadedFile
from spudmart.utils.cover_image import reset_cover_image, save_cover_image_from_request
from spudderkrowdio.utils import start_following, stop_following, get_following, post_comment
from spudmart.venues.models import Venue


def landing_page(request):
    template_data = {}
    template_data['find_teams'] = TeamPage.objects.all()[:10]
    template_data['find_fans'] = FanPage.objects.all()[:10]
    if is_fan(request.current_role):
        stream = SpudsController(request.current_role).get_spud_stream() + SpudsController.GetSpudsForFan(request.current_role.entity)
        shuffle(stream)
        template_data['spuds'] = stream
        krowdio_response = get_following(request.current_role)
        template_data['teams'] = krowdio_users_to_links(request.can_edit, request.current_role, krowdio_response['data'], 'team')
        template_data['fans'] = krowdio_users_to_links(request.can_edit, request.current_role, krowdio_response['data'], 'fan')
        tags = FanFollowingEntityTag.objects.filter(fan=request.current_role.entity)
        template_data['tags'] = [(t.tag, t.get_entity_icon()) for t in tags]
    return render(request, 'spudderspuds/pages/landing_page.html', template_data)


def entity_search(request, entity_type):
    template_data = {'entity_type': entity_type}
    if entity_type == "fan":
        fans = FanPage.objects
        template_data['entities'] = fans.exclude(fan=request.user) if request.current_role else fans.all()
    if entity_type == "team":
        template_data['entities'] = TeamPage.objects.all()
    return render(request, 'spudderspuds/pages/entity_search.html', template_data)


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
    fan_role = RoleFan(page)
    krowdio_response = get_following(fan_role)
    template_data = {
        'page': page, 'fan_spuds': SpudsController.GetSpudsForFan(page),
        'base_url': 'spudderspuds/base.html',
        'following_teams': krowdio_users_to_links(request.can_edit, fan_role, krowdio_response['data'], 'team'),
                'following_fans': krowdio_users_to_links(request.can_edit, fan_role, krowdio_response['data'], 'fan')}
    if request.can_edit:
        template_data['following_teams_title'] = "<img src='/static/img/spudderspuds/button-teams-tiny.png' /> Teams You Follow"
        template_data['following_fans_title'] = "<img src='/static/img/spudderspuds/button-fans-tiny.png' /> Fans You Follow"
    else:
        template_data['following_teams_title'] = "<img src='/static/img/spudderspuds/button-teams-tiny.png' /> Teams %s Follows" % page.name
        template_data['following_fans_title'] = "<img src='/static/img/spudderspuds/button-fans-tiny.png' /> Fans %s Follows" % page.name

    if is_fan(request.current_role):
        tags = FanFollowingEntityTag.objects.filter(fan=request.current_role.entity)
        template_data['tags'] = [(t.tag, t.get_entity_icon()) for t in tags]

    return render(request, 'spudderspuds/fans/pages/fan_page_view.html', template_data)


def fan_profile_edit(request, page_id):
    fan_page = get_object_or_404(FanPage, pk=page_id)
    profile_form = FanPageForm(initial=fan_page.__dict__)
    social_accounts_form = FanPageSocialMediaForm(initial=fan_page.__dict__)
    if request.method == 'POST':
        profile_form = FanPageForm(request.POST)
        social_accounts_form = FanPageSocialMediaForm(request.POST)
        if profile_form.is_valid() and social_accounts_form.is_valid():
            for attr in ('name', 'date_of_birth', 'state', ):
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
    if spud.state == SpudFromSocialMedia.STATE_ACCEPTED:  # Don't allow dupes!
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


def follow(request):
    """
    A page allowing the Fan to create a custom #tag for entity
    :param request: a GET request
    :return: a single well with form for entity #tag, or an
        HTTPResponseNotAllowed
    """
    if request.method == 'GET':
        origin = str(request.GET.get('origin', ''))
        name = tag = base_well_url = base_quote_url = None
        fan_tags = FanFollowingEntityTag.objects.filter(fan=request.current_role.entity)

        if re.match(r'/venues/view/\d+', origin):
            ven = Venue.objects.get(id=str.split(origin, '/')[-1])
            name = ven.aka_name
            tag = ven.name
            base_well_url = 'spuddercern/base_single_well.html'
            base_quote_url = 'spuddercern/quote_messages/base_quote_message.html'

        elif re.match(r'/fan/\d+', origin):
            fan = FanPage.objects.get(id=str.split(origin, '/')[-1])
            name = fan_page_name(fan)
            tag = name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'

        elif re.match(r'/team/\d+', origin):
            team = TeamPage.objects.get(id=str.split(origin, '/')[-1])
            name = team.name
            tag = team.at_name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'

        elif re.match(r'/team/create', origin):
            team = TeamPage.objects.get(id=request.GET.get('team_id'))
            name = team.name
            tag = team.at_name
            base_well_url = 'spudderspuds/base_single_well.html'
            base_quote_url = 'spudderspuds/components/base_quote_message.html'
            origin = "/team/%s" % team.id
            messages.success(
                request,
                "<h4><i class='fa fa-check'></i> Team %s successfully created!</h4>"
                "<p>You successfully create your new team, now please give them a custom #tag</p>" % team.name)

        template_data = {
            'name': name,
            'tag': tag,
            'base_well_url': base_well_url,
            'base_quote_url': base_quote_url,
            'origin': origin,
            'fan_tags': fan_tags}
        return render(request, 'components/sharedpages/following/start_following.html', template_data)

    else:
        return HttpResponseNotAllowed(['GET'])


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
        tag = str(request.POST.get('tag', None)) or request.POST['base_tag']  # if empty use the entity name
        if re.match(r'/venues/view/\d+', origin):
            entity_type = EntityController.ENTITY_VENUE
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+', origin):
            entity_type = RoleController.ENTITY_FAN
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/\d+', origin):
            entity_type = EntityController.ENTITY_TEAM
            entity_id = str.split(origin, '/')[-1]
            team = TeamPage.objects.get(id=entity_id)
            admin = TeamAdministrator.objects.get(team_page=team)
            stu = Student.objects.get(id=admin.entity_id)
            team_gained_follower(stu)

        entity_tag = FanFollowingEntityTag(
            fan=request.current_role.entity,
            tag=tag,
            entity_id=entity_id,
            entity_type=entity_type)
        entity_tag.save()

        json = start_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def stop_following_view(request):
    """
    Current role (fan) stops following entity in request
    :param request: a POST request
    :return: the response from the KrowdIO API on success,
        or an HttpResponseNotAllowed response
    """
    if request.method == 'POST':
        origin = str(request.POST.get('origin', ''))
        entity_id = entity_type = None
        if re.match(r'/venues/view/\d+', origin):
            entity_type = EntityController.ENTITY_VENUE
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/fan/\d+', origin):
            entity_type = RoleController.ENTITY_FAN
            entity_id = str.split(origin, '/')[-1]
        elif re.match(r'/team/\d+', origin):
            entity_type = EntityController.ENTITY_TEAM
            entity_id = str.split(origin, '/')[-1]

        fan_tag = FanFollowingEntityTag.objects.get(
            fan=request.current_role.entity,
            entity_type=entity_type,
            entity_id=entity_id)
        fan_tag.delete()

        json = stop_following(request.current_role, entity_type, entity_id)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])


def krowdio_users_to_links(can_edit, current_role, krowdio_dict, filter=None):
    """
    Translates KrowdIO users into a list of dicts about Spudder entities
    :param krowdio_dict: the 'users' part of a response from the
        KrowdIO API (intended for use with followers/following)
    :return: a list of dicts, where the dict contains the icon link,
        profile link, and name of each Spudder entity followed
    """
    users = []
    for user in krowdio_dict:
        krowdio_id = user['_id']
        storage_obj = KrowdIOStorage.objects.get(krowdio_user_id=krowdio_id)
        if storage_obj.role_id:
            if storage_obj.role_type == 'fan' and (filter == 'fan' or filter is None):
                fan = FanPage.objects.get(id=storage_obj.role_id)
                if fan.avatar:
                    icon_link = '/file/serve/%s' % fan.avatar.id
                else:
                    icon_link = '/static/img/spudderfans/button-fans-tiny.png'
                users.append({
                    'name': fan.name,
                    'profile': '/fan/%s' % fan.id,
                    'icon_link': icon_link,
                    'custom_tag': FanFollowingEntityTag.GetTag(
                        fan=current_role.entity,
                        entity_id=fan.id,
                        entity_type=RoleController.ENTITY_FAN) if can_edit else None
                })
            elif storage_obj.role_type == 'sponsor' and (filter == 'sponsor' or filter is None):
                sponsor = SponsorPage.objects.get(id=storage_obj.role_id)
                if sponsor.thumbnail:
                    icon_link = '/file/serve/%s' % sponsor.thumbnail
                else:
                    icon_link = '/static/img/spuddersponsors/button-sponsors-tiny.png'
                users.append({
                    'name': sponsor.name,
                    'profile': '/sponsor/%s' % sponsor.id,
                    'icon_link': icon_link,
                    'custom_tag': FanFollowingEntityTag.GetTag(
                        fan=current_role.entity,
                        entity_id=sponsor.id,
                        entity_type=RoleController.ENTITY_SPONSOR) if can_edit else None
                })
            elif storage_obj.role_type == 'student' and (filter == 'student' or filter is None):
                stu = Student.objects.get(id=storage_obj.role_id)
                if stu.logo:
                    icon_link = '/file/serve/%s' % stu.logo
                else:
                    icon_link = 'static/img/spuddercern/button-cern-tiny.png'
                users.append({
                    'name': user_name(stu.user),
                    'profile': '/cern/student/%s' % stu.id,
                    'icon_link': icon_link,
                    'custom_tag': FanFollowingEntityTag.GetTag(
                        fan=current_role.entity,
                        entity_id=stu.id,
                        entity_type=RoleController.ENTITY_STUDENT) if can_edit else None
                })
        elif storage_obj.venue:
            if storage_obj.venue.logo and (filter == 'venue' or filter is None):
                icon_link = '/file/serve/%s' % storage_obj.venue.logo.id
            else:
                icon_link = '/static/img/spudderspuds/button-spuds-tiny.png'
            users.append({
                'name': storage_obj.venue.aka_name,
                'profile': '/venues/view/%s' % storage_obj.venue.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=storage_obj.venue.id,
                    entity_type=EntityController.ENTITY_VENUE) if can_edit else None
            })
        elif storage_obj.team and (filter == 'team' or filter is None):
            if storage_obj.team.image:
                icon_link = '/file/serve/%s' % storage_obj.team.image.id
            else:
                icon_link = '/static/img/spudderspuds/button-teams-tiny.png'
            users.append({
                'name': storage_obj.team.name,
                'profile': '/team/%s' % storage_obj.team.id,
                'icon_link': icon_link,
                'custom_tag': FanFollowingEntityTag.GetTag(
                    fan=current_role.entity,
                    entity_id=storage_obj.team.id,
                    entity_type=EntityController.ENTITY_TEAM) if can_edit else None
            })
    return users


def test_spuds(request):
    template_data = {}
    if is_fan(request.current_role):
        stream = SpudsController(request.current_role).get_spud_stream() + SpudsController.GetSpudsForFan(
            request.current_role.entity)
        shuffle(stream)
        template_data['spuds'] = stream
        tags = FanFollowingEntityTag.objects.filter(fan=request.current_role.entity)
        template_data['tags'] = [(t.tag, t.get_entity_icon()) for t in tags]
        return render(request, 'spudderspuds/pages/test_spuds.html', template_data)


def add_spud_comment(request):
    """
    Adds a comment to a SPUD (KrowdIO post) that tags Spudder entities
    :param request: a POST request
    :return: response from KrowdIO or HttpResponseNotAllowed
    """
    if request.method == 'POST':
        entity = KrowdIOStorage.GetOrCreateForCurrentUserRole(
            user_role=request.current_role)
        spud_id = request.POST.get('spud_id')
        tags = request.POST.getlist('tags[]')

        text = ""
        fan = request.current_role.entity
        for t in tags:
            tag = FanFollowingEntityTag.objects.get(fan=fan, tag=t)
            text += "@%s%s " % (tag.entity_type, tag.entity_id)
            if tag.entity_type == 'Team':
                team = TeamPage.objects.get(id=tag.entity_id)
                admin = TeamAdministrator.objects.get(team_page=team)
                if admin.entity_type == 'student':
                    stu = Student.objects.get(id=admin.entity_id)
                    team_tagged_in_spud(stu)

        json = post_comment(entity, spud_id, text)
        return HttpResponse(simplejson.dumps(json))
    else:
        return HttpResponseNotAllowed(['POST'])