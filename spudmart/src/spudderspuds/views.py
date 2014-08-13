from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.templatetags.spudderaccountstags import is_fan, user_has_fan_role
from spudderspuds.forms import FanSigninForm, FanRegisterForm
from spudderspuds.utils import create_and_activate_fan_role


def landing_page(request):
    return render(request, 'spudderspuds/pages/landing_page.html')


def user_signin(request):
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


def user_register(request):
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
            create_and_activate_fan_role(request, user)
            login(request, authenticate(username=username, password=password))
            return redirect('/spuds')
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
    create_and_activate_fan_role(request, request.user)
    return redirect('/spuds/register_add_fan_role/complete')


def user_add_fan_role_complete(request):
    template_data = {}
    return render_to_response(
        'spudderspuds/pages/user_register_add_fan_role_complete.html',
        template_data,
        context_instance=RequestContext(request))

