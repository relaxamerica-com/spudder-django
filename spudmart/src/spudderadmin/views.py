from django.http import HttpResponse
from django.shortcuts import render_to_response
from spudderadmin.decorators import admin_login_required


def admin_login(request):
    return render_to_response(
        'spudderadmin/base.html'
    )

@admin_login_required
def admin_dashboard(request):
    return HttpResponse('dashboard')