from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext
from django.views.defaults import page_not_found
from spudderaccounts.controllers import InvitationController
from spudderaccounts.models import Invitation
from spudderaccounts.templatetags.spudderaccountstags import is_fan
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderaffiliates.decorators import affiliate_login_required
from spudderaffiliates.forms import ClubAdministratorForm
from spudderaffiliates.models import Affiliate
from spudderdomain.controllers import SpudsController, RoleController, EntityController
from spudderdomain.models import TeamPage, FanPage, Club, TempClub
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


@affiliate_login_required
def invite_club_manager(request):
    """
    Invites users to create a club
    :param request: any request
    :return: a simple form to add a club administrator from email
    """
    if feature_is_enabled('invite_clubs'):
        if request.method == 'POST':
            form = ClubAdministratorForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                name = form.cleaned_data.get('club_name')
                state = form.cleaned_data.get('state')
                fan = InvitationController.CheckFanWithEmailExists(email)
                club = TempClub(email=email, name=name, state=state)
                club.save()
                aff = request.session['affiliate']
                if fan:
                    InvitationController.InviteEntity(fan.id,
                                                      RoleController.ENTITY_FAN,
                                                      Invitation.AFFILIATE_INVITE_CLUB_ADMINISTRATOR,
                                                      club.id,
                                                      EntityController.ENTITY_TEMP_CLUB,
                                                      extras={'affiliate_name': aff.name})
                else:
                    InvitationController.InviteNonUser(email,
                                                       Invitation.AFFILIATE_INVITE_CLUB_ADMINISTRATOR,
                                                       club.id,
                                                       EntityController.ENTITY_TEMP_CLUB,
                                                       extras={'affiliate_name': aff.name})

                messages.success(request, "%s invited to administer club \"%s\"" %
                                 (email, name))
                form = ClubAdministratorForm()
        else:
            form = ClubAdministratorForm()
        return render(request,
                      'spudderaffiliates/pages/invite_club.html',
                      {
                          'form': form
                      })
    else:
        raise Http404


def invitation(request):
    """
    Acceptance page for invitation.
    :param request: any request
    :return: a place to register if not a user and to create a club
        associated with affiliate if are a user
    """
    return render_to_response('spudderaffiliates/pages/accept_invitation.html',
                              context_instance=RequestContext(request))