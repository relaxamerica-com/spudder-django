from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from spudderaccounts.wrappers import RoleStudent
from spudderadmin.decorators import admin_login_required
from spudderadmin.utils import encoded_admin_session_variable_name
from spudmart.CERN.models import Student


def admin_login(request):
    error = False
    if request.method == 'POST':
        error = True
        if request.POST.get('username', None) == 'admin@spudder.com' and \
           request.POST.get('password', None) == 'spudmart1':
            request.session[encoded_admin_session_variable_name()] = True
            return redirect(admin_dashboard)
    return render_to_response(
        'spudderadmin/pages/login.html',
        {'error': error},
        context_instance=RequestContext(request))


@admin_login_required
def admin_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/dashboard.html',
        {},
        context_instance=RequestContext(request))


@admin_login_required
def cern_dashboard(request):
    return render_to_response(
        'spudderadmin/pages/cern/dashboard.html',
        {
            'students': [RoleStudent(s) for s in Student.objects.all()]
        },
        context_instance=RequestContext(request))
