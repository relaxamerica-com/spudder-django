import urlparse
from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.views.generic import RedirectView
from spudderdomain.controllers import RoleController
from spudderspuds.forms import FanSigninForm

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'djangotoolbox.errorviews.server_error'


def temp_redirect_view(request):
    """
    Redirects the root to info.spudder.com and handles any funky sub-domains

    This is a temp solution to this problem and should be replaced with A and C name changes at the DNS level, but ...
    it will do for now :) MG 20140618

    :param request: the request object
    :return: HttpResponseRedirect object
    """
    redirect_url = None

    if hasattr(request, 'META'):
        try:
            url_parts = request.META['HTTP_HOST'].split('.')
            if len(url_parts) > 1:
                if url_parts[0] == "cern":
                    redirect_url = "http://www.spudder.com/cern/"
                if url_parts[0] == "spudder" and url_parts[1] == "com":
                    redirect_url = "http://www." + ",".join(url_parts)
                if redirect_url:
                    return HttpResponseRedirect(redirect_url)
        except KeyError:
            pass  # request META dict doesn't have HTTP_HOST key (f.i. in tests)

    # Deal with current role if one exists
    if request.current_role:
        if request.current_role.entity_type == RoleController.ENTITY_FAN:
            return HttpResponseRedirect('/spuds')
        if request.current_role.entity_type == RoleController.ENTITY_STUDENT:
            return HttpResponseRedirect('/cern')
        if request.current_role.entity_type == RoleController.ENTITY_SPONSOR:
            return HttpResponseRedirect('/sponsor')

    template_data = {
        'signin_form': FanSigninForm()
    }
    return render(request, 'main_splash.html', template_data)

urlpatterns = patterns(
    '',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^_ah/start$', 'spudmart.utils.backends.start'),
    # (r'^$', include('spudmart.home.urls')),  NOTE: Commented out by MG 20140617
    (r'^dashboard/recipient/', include('spudmart.recipients.urls')),
    (r'^dashboard/donation/', include('spudmart.donations.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('spudmart.accounts.urls')),
    (r'^venues/', include('spudmart.venues.urls')),
    (r'^spudder/', include('spudmart.spudder.urls')),
    (r'^upload/', include('spudmart.upload.urls')),
    (r'^sponsor', include('spudmart.sponsors.urls')),
    (r'^team/', include('spudmart.teams.urls')),
    (r'^hospitals/', include('spudmart.hospitals.urls')),
    (r'^file/serve/(?P<file_id>\d+)$', 'spudmart.upload.views.serve_uploaded_file'),
    (r'^api/1/', include('spudmart.api.urls')),

    url(r'^cern/', include('spudmart.CERN.urls')),
    url(r'^users/', include('spudderaccounts.urls')),
    url(r'^spuds/', include('spudderspuds.urls_spuds')),
    url(r'^fan/', include('spudderspuds.urls_fans')),
    url(r'^flag/', include('spudmart.flags.urls')),
    url(r'^club/', include('spudderclubs.urls')),
    url(r'^challenges/', include('spudmart.challenges.urls')),

    # Spudder Admin site
    (r'^spudderadmin', include('spudderadmin.urls')),

    # Spudder Social Engine Urls
    (r'^socialengine/', include('spuddersocialengine.urls')),

    # @postspud short urls
    (r'^s/', include('spudderspuds.urls_spuds')),

    # Legacy URL mapping
    (r'^campusrep', RedirectView.as_view(url="/cern/")),
    (r'^privacy', RedirectView.as_view(url="http://info.spudder.com/privacy/")),

    # Note the below line was added to catch root urls and push them to info.spudder.com for now MG 20140618
    (r'^$', temp_redirect_view)
)