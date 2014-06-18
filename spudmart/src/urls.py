import urlparse
from django.conf.urls.defaults import *
from django.http import HttpResponseRedirect

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
    redirect_url = "http://info.spudder.com"
    url_parts = request.META['HTTP_HOST'].split('.')
    if len(url_parts) > 1:
        if url_parts[0] == "cern":
            redirect_url = "/cern/"
    return HttpResponseRedirect(redirect_url)

urlpatterns = patterns(
    '',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^_ah/start$', 'spudmart.utils.backends.start'),
    # (r'^$', include('spudmart.home.urls')),  NOTE: Commented out by MG 20140617
    (r'^dashboard/recipient/', include('spudmart.recipients.urls')),
    (r'^dashboard/donation/', include('spudmart.donations.urls')),
    (r'^dashboard/sponsor/', include('spudmart.sponsors.urls')),
    (r'^dashboard/', include('spudmart.dashboard.urls')),
    (r'^accounts/', include('spudmart.accounts.urls')),
    (r'^venues/', include('spudmart.venues.urls')),
    (r'^spudder/', include('spudmart.spudder.urls')),
    (r'^upload/', include('spudmart.upload.urls')),
    (r'^sponsor/', include('spudmart.sponsors.public_urls')),
    (r'^hospitals/', include('spudmart.hospitals.urls')),
    (r'^file/serve/(?P<file_id>\d+)$', 'spudmart.upload.views.serve_uploaded_file'),
    (r'^api/1/', include('spudmart.api.urls')),

    (r'^cern/', include('spudmart.CERN.urls')),

    # Note the below line was added to catch root urls and push them to info.spudder.com for now MG 20140618
    (r'^$', temp_redirect_view)
)
