from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.forms import ProfileDetailsForm
from spudderdomain.controllers import RoleController
from spudderaccounts.wrappers import EntityStudent


def accounts_signin(request):
    return render_to_response('spudderaccounts/base.html')


@login_required(login_url='/accounts/signin')
def accounts_dashboard(request):
    role_controller = RoleController(request.user)
    user_roles = []
    for pair in ((RoleController.ENTITY_STUDENT, EntityStudent), ):
        user_roles += role_controller.roles_by_entity(pair[0], pair[1])
    user_roles.sort(key=lambda r: r.meta_data.get('last_accessed', 0), reverse=True)
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
def accounts_manage_role(request, role_type, entity_id):
    role_controller = RoleController(request.user)
    if role_type == RoleController.ENTITY_STUDENT:
        role = role_controller.role_by_entity_type_and_entity_id(role_type, entity_id, EntityStudent)
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
