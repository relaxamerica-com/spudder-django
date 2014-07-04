from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.forms import ProfileDetailsForm
from spudderaccounts.utils import select_all_user_roles
from spudderdomain.controllers import RoleController
from spudderaccounts.wrappers import RoleBase


def accounts_signin(request):
    return render_to_response('spudderaccounts/base.html')


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
    next_url = request.GET.get('next', None)
    request.session['current_role'] = {'entity_type': entity_type, 'entity_id': entity_id}
    return redirect(next_url or '/users')


def accounts_add_role(request):
    return render_to_response(
        'spudderaccounts/pages/add_new_role.html',
        {},
        context_instance=RequestContext(request))


def accounts_create_role(request, entity_type):
    pass  # TODO: working here MG: 20140704