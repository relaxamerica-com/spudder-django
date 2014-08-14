from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderdomain.controllers import TeamsController, RoleController
from spudderdomain.models import FanPage
from spudderspuds.forms import FanSigninForm, FanRegisterForm, FanPageForm
from spudderspuds.utils import create_and_activate_fan_role
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
            return redirect('/spuds')
    else:
        form = FanSigninForm()
    template_data["form"] = form
    return render_to_response(
        'spudderspuds/pages/user_signin.html',
        template_data,
        context_instance=RequestContext(request))


def fan_register(request):
    if request.current_role and request.current_role.entity_type == RoleController.ENTITY_FAN:
        return redirect('/spuds')
    if request.current_role and not is_fan(request.current_role) and not user_has_fan_role(request):
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
    return render(request, 'spudderspuds/fans/pages/fan_page_view.html', {
        'page': page,
        'can_edit': request.current_role.entity.id == page.id
    })


def fan_profile_edit(request, page_id):
    fan_page = get_object_or_404(FanPage, pk=page_id)
    form = FanPageForm(initial=fan_page.__dict__)
    if request.method == 'POST':
        form = FanPageForm(request.POST)
        if form.is_valid():
            for attr in ('name', 'last_name', 'date_of_birth', ):
                fan_page.__setattr__(attr, form.cleaned_data[attr])
            fan_page.save()
        return redirect('/fan/%s' % fan_page.id)
    #     updated_page = form.save(False)
    #     updated_page.fan = request.user
    #     updated_page.save()
    #     next_url = request.POST.get('next_url', '')
    # page = get_object_or_404(FanPage, pk=page_id)
    return render(request, 'spudderspuds/fans/pages/fan_page_edit.html', {
        'form': form,
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

