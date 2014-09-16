from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.views.defaults import page_not_found
from spudderaccounts.templatetags.spudderaccountstags import is_fan
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderaffiliates.decorators import affiliate_login_required
from spudderaffiliates.models import Affiliate
from spudderdomain.controllers import SpudsController, RoleController, EntityController
from spudderdomain.models import TeamPage, FanPage, Club
from spudderkrowdio.utils import get_following
from spudderspuds.views import krowdio_users_to_links
from spudmart.venues.models import Venue


def _nays_survey(request):
    return render(request, 'spudderaffiliates/pages/_nays_survey.html')


def affiliate_login(request):
    if feature_is_enabled('affiliate_login'):
        error = False
        if request.method == 'POST':
            username = request.POST.get('username', None)
            password = request.POST.get('password', None)
            try:
                aff = Affiliate.objects.get(username=username, password=password)
            except Affiliate.DoesNotExist:
                error = True
            else:
                request.session['affiliate'] = aff
                return redirect(affiliate_dashboard)
        return render_to_response(
            'spudderaffiliates/pages/login.html',
            {'error': error},
            context_instance=RequestContext(request))
    else:
        raise Http404


def affiliate_splash(request, affiliate_url_name):
    """
    Gives affiliate splash page
    :param request: any request
    :param affiliate_url_name: any string without the \ character,
        formatted to lowercase for URL matching
    :return: an affiliate's splash page, or a 404 error if not a valid
        affiliate URL
    """
    if affiliate_url_name:
        affiliate_url_name = affiliate_url_name.lower()
    if affiliate_url_name and affiliate_url_name == 'nays' and feature_is_enabled('nays_survey'):
        return _nays_survey(request)

    try:
        aff = Affiliate.objects.get(url_name=affiliate_url_name)
    except Affiliate.DoesNotExist:
        raise Http404
    else:
        template_data = {
            'find_teams': TeamPage.objects.filter(affiliate=aff)[:10],
            'find_fans': FanPage.objects.filter(affiliate=aff)[:10],
            'find_clubs': Club.objects.filter(affiliate=aff)[:10],
            'affiliate': aff
        }
        if is_fan(request.current_role):
            spud_stream = SpudsController(request.current_role).get_spud_stream()
            fan_spuds = SpudsController.GetSpudsForFan(request.current_role.entity)
            stream = SpudsController.MergeSpudLists(spud_stream, fan_spuds)
            template_data['spuds'] = stream
            krowdio_response = get_following(request.current_role)
            template_data['teams'] = krowdio_users_to_links(
                request.can_edit,
                request.current_role,
                krowdio_response['data'],
                EntityController.ENTITY_TEAM)
            template_data['fans'] = krowdio_users_to_links(
                request.can_edit,
                request.current_role,
                krowdio_response['data'],
                RoleController.ENTITY_FAN)
            template_data['fan_nav_active'] = "explore"
        return render(request,
                      'spudderaffiliates/pages/landing_page.html',
                      template_data)

@affiliate_login_required
def affiliate_dashboard(request):
    """
    Displays the affiliate dashboard
    :param request: any request
    :return: a simple dashboard with affiliate data overview
    """
    if feature_is_enabled('affiliate_login'):
        return render(request, 'spudderaffiliates/pages/dashboard.html')
    else:
        raise Http404