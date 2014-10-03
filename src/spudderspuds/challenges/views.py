import json
import logging
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from google.appengine.api import blobstore, taskqueue
from spudderaccounts.controllers import NotificationController
from spudderaccounts.models import Notification
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderkrowdio.models import FanFollowingEntityTag
from spudderkrowdio.utils import start_following
from spudderspuds.utils import create_and_activate_fan_role
from spudmart.CERN.models import STATES
from spudderdomain.models import Club, TempClub, FanPage, Challenge, ChallengeTemplate, ChallengeParticipation, \
    ClubAdministrator, TeamPage, TeamAdministrator, TeamClubAssociation
from spudderdomain.models import ChallengeChallengeParticipation
from spudmart.upload.forms import UploadForm
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleBase, RoleFan
from spudderdomain.wrappers import EntityBase
from spudderdomain.controllers import RoleController, EntityController, CommunicationController
from spudderspuds.challenges.forms import CreateTempClubForm, ChallengeConfigureForm, ChallengesRegisterForm, \
    RegisterCreateClubForm
from spudderspuds.challenges.forms import ChallengesSigninForm, AcceptChallengeForm, UploadImageForm
from spudderspuds.challenges.forms import ChallengeChallengeParticipationForm
from spudderspuds.challenges.models import TempClubOtherInformation, ChallengeTree, ChallengeServiceConfiguration
from spudderspuds.challenges.models import ChallengeServiceMessageConfiguration


def _get_clubs_by_state(state):
    clubs = [c for c in Club.objects.filter(state=state)]
    for x in range(len(clubs)):
        clubs[x] = clubs[x].__dict__
        clubs[x]['type'] = 'o'
    temp_club = [c for c in TempClub.objects.filter(state=state)]
    for x in range(len(temp_club)):
        temp_club[x] = temp_club[x].__dict__
        temp_club[x]['type'] = 't'
    clubs = [c for c in clubs] + [c for c in temp_club]
    clubs.sort(key=lambda x: x['name'])
    return clubs


def _create_temp_club(form, state):
    name = form.cleaned_data['name'].upper()
    email = form.cleaned_data['email']
    other_info = form.cleaned_data['other_information']
    website = form.cleaned_data['website']
    contact_number = form.cleaned_data['contact_number']
    temp_club, created = TempClub.objects.get_or_create(name=name, state=state)
    temp_club.email = email or temp_club.email
    temp_club.save()
    if other_info or website or contact_number:
        temp_club_other_info, created = TempClubOtherInformation.objects.get_or_create(temp_club=temp_club)
        temp_club_other_info.other_information = other_info
        temp_club_other_info.website = website
        temp_club_other_info.contact_number = contact_number
        temp_club_other_info.save()
    return temp_club


def _create_challenge(club_class, club_id, form, request, template, parent=None, image=None, youtube_video_id=None):
    donation_accept = form.cleaned_data.get('donation_with_challenge')
    donation_reject = form.cleaned_data.get('donation_without_challenge')
    recipient_entity_type = EntityController.ENTITY_CLUB
    if club_class == TempClub:
        recipient_entity_type = EntityController.ENTITY_TEMP_CLUB
    challenge = Challenge(
        template=template,
        name=template.name,
        description=template.description,
        creator_entity_id=request.current_role.entity.id,
        creator_entity_type=request.current_role.entity_type,
        recipient_entity_id=club_id,
        recipient_entity_type=recipient_entity_type,
        proposed_donation_amount=donation_accept,
        proposed_donation_amount_decline=donation_reject)
    challenge.save()
    if parent or image or youtube_video_id:
        if parent:
            challenge.parent = parent
        if image:
            challenge.image = image
        if youtube_video_id:
            challenge.youtube_video_id = youtube_video_id
        challenge.save()
    if feature_is_enabled('challenge_tree'):
        if parent is None:
            ChallengeTree.CreateNewTree(challenge)
        else:
            ChallengeTree.AddChallengeToTree(challenge)
    return challenge


def challenges_splash(request):
    template_data = {}
    return render(request, 'spudderspuds/challenges/pages/challenges.html', template_data)


def create_signin(request):
    form = ChallengesSigninForm(initial=request.GET)
    if request.method == "POST":
        form = ChallengesSigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            fan = FanPage.objects.filter(fan=user)[0]
            change_current_role(request, RoleController.ENTITY_FAN, fan.id)
            return redirect(form.cleaned_data.get('next', '/'))
    return render(
        request,
        'spudderspuds/challenges/pages/signin.html',
        {'form': form})


def create_register(request):
    form = ChallengesRegisterForm(initial=request.GET)
    if request.method == "POST":
        form = ChallengesRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('email_address')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username, username, password)
            user.save()
            user.spudder_user.mark_password_as_done()
            fan_entity = create_and_activate_fan_role(request, user)
            fan_page = fan_entity.entity
            fan_page.username = form.cleaned_data.get('username')
            fan_page.state = form.cleaned_data.get('state')
            fan_page.save()
            login(request, authenticate(username=username, password=password))
            if form.cleaned_data.get('account_type') == EntityController.ENTITY_CLUB:
                return redirect('/challenges/register/team?next=%s' % form.cleaned_data.get('next', '/'))
            return redirect(form.cleaned_data.get('next', '/'))
    return render(
        request,
        'spudderspuds/challenges/pages/register.html',
        {'form': form})


def register_club(request):
    form = RegisterCreateClubForm(initial=request.GET)
    if request.method == 'POST':
        form = RegisterCreateClubForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            name = data.get('name')
            at_name = data.get('at_name')
            sport = data.get('sport')
            description = data.get('description')
            state = data.get('state')
            address = data.get('address')
            club = Club(name=name, address=address, description=description, state=state)
            club.save()
            club_admin = ClubAdministrator(club=club, admin=request.user)
            club_admin.save()
            team = TeamPage(name=name, at_name=at_name, free_text=description, state=state, sport=sport)
            team.save()
            team_admin = TeamAdministrator(
                entity_type=request.current_role.entity_type,
                entity_id=request.current_role.entity.id,
                team_page=team)
            team_admin.save()
            tca = TeamClubAssociation(team_page=team, club=club)
            tca.save()
            following_tag = FanFollowingEntityTag(
                fan=request.current_role.entity,
                tag=at_name,
                entity_id=team.id,
                entity_type=EntityController.ENTITY_TEAM)
            following_tag.save()
            start_following(request.current_role, EntityController.ENTITY_TEAM, team.id)
            return redirect(form.cleaned_data.get('next', '/'))
    return render(
        request,
        'spudderspuds/challenges/pages/register_create_club.html',
        {'form': form})


def create_challenge(request):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s' % request.path)
    template_data = {'templates': ChallengeTemplate.objects.filter(active=True)}
    return render(request, 'spudderspuds/challenges/pages/create_challenge_choose_template.html', template_data)


def create_challenge_choose_club_choose_state(request, template_id):
    template_data = {
        'template': get_object_or_404(ChallengeTemplate, id=template_id),
        'states': [{'id': '', 'name': 'Select a state ...'}] + sorted([
            {'id': k, 'name': v} for k, v in STATES.items()], key=lambda x: x['id'])}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_choose_club_choose_state.html',
        template_data)


def create_challenge_choose_club(request, template_id, state):
    template_data = {
        'state': STATES[state],
        'template': get_object_or_404(ChallengeTemplate, id=template_id),
        'clubs': _get_clubs_by_state(state)}
    return render(
        request,
        'spudderspuds/challenges/components/create_challenge_choose_club.html',
        template_data)


def create_challenge_choose_club_create_club(request, template_id, state):
    form = CreateTempClubForm()
    if request.method == 'POST':
        form = CreateTempClubForm(request.POST)
        if form.is_valid():
            temp_club = _create_temp_club(form, state)
            return redirect('/challenges/create/%s/%s/t/%s' % (template_id, state, temp_club.id))
    template_data = {
        'form': form,
        'state': STATES[state],
        'template': get_object_or_404(ChallengeTemplate, id=template_id)}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_choose_club_create_club.html',
        template_data)


def create_challenge_set_donation(request, template_id, state, club_id, club_class):
    club = get_object_or_404(club_class, id=club_id)
    template = get_object_or_404(ChallengeTemplate, id=template_id)
    form = ChallengeConfigureForm()
    upload_url = blobstore.create_upload_url('/challenges/create/%s/%s/%s/%s' % (
        template_id, state, 'o' if club_class == Club else 't', club_id))
    if request.method == 'POST':
        form = ChallengeConfigureForm(request.POST)
        if form.is_valid():
            uploaded_file = None
            if request.FILES:
                upload_form = UploadForm(request.POST, request.FILES)
                uploaded_file = upload_form.save()
            challenge = _create_challenge(club_class, club_id, form, request, template, image=uploaded_file)
            redirect_url = '/challenges/%s/share' % challenge.id
            if request.is_ajax():
                return HttpResponse(redirect_url)
            return redirect(redirect_url)
        if request.is_ajax():
            return HttpResponse("%s|%s" % (
                blobstore.create_upload_url(upload_url),
                '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
    template_data = {
        'club': club,
        'club_class': club_class.__name__,
        'form': form,
        'state': state,
        'template': template,
        'upload_url': upload_url}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_configure.html',
        template_data)


def challenge_share(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    template_data = {'challenge': challenge, 'template': template}
    return render(request, 'spudderspuds/challenges/pages/challenge_share.html', template_data)


def challenge_view(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    template_data = {
        'challenge': challenge,
        'template': template,
        'owner': RoleController.GetRoleForEntityTypeAndID(
            challenge.creator_entity_type,
            challenge.creator_entity_id,
            RoleFan)}
    if feature_is_enabled('challenge_tree'):
        challenge_tree = ChallengeTree.GetChallengeTree(challenge).get_tree()
        challenge_tree_data = challenge_tree.to_dict()
        beneficiaries_data = challenge_tree.update_beneficiaries_data()
        template_data['challenge_tree'] = json.dumps(challenge_tree_data)
        template_data['beneficiaries'] = beneficiaries_data
    return render(request, 'spudderspuds/challenges/pages/challenge_view.html', template_data)


def challenge_accept_notice(request, challenge_id):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s' % request.path)
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation, created = ChallengeParticipation.objects.get_or_create(
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    participation.state = ChallengeParticipation.PRE_ACCEPTED_STATE
    participation.save()
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary,
        'participation': participation}
    return render(request, 'spudderspuds/challenges/pages/challenge_accept_notice.html', template_data)


def challenge_accept_pledge(request, challenge_id):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s' % request.path)
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    form = AcceptChallengeForm(initial={'donation': int(challenge.proposed_donation_amount)})
    if request.method == 'POST':
        form = AcceptChallengeForm(request.POST)
        if form.is_valid():
            participation, created = ChallengeParticipation.objects.get_or_create(
                challenge=challenge,
                participating_entity_id=request.current_role.entity.id,
                participating_entity_type=request.current_role.entity_type)
            participation.donation_amount = form.cleaned_data.get('donation', 0)
            participation.state = ChallengeParticipation.DONATE_ONLY_STATE
            participation.save()
            if feature_is_enabled('challenge_tree'):
                ChallengeTree.AddParticipationToTree(challenge, participation)
            redirect_url = '/challenges/%s/accept/notice?just_pledged=True' % challenge.id
            return redirect(redirect_url)
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary,
        'form': form}
    return render(request, 'spudderspuds/challenges/pages/challenge_accept_pledge.html', template_data)


def challenge_accept_upload(request, challenge_id):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s' % request.path)
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation = ChallengeParticipation.objects.get(
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    redirect_url = '/challenges/%s/beneficiary/%s?just_pledged=True' % (participation.id, beneficiary.state)
    action_upload_image = 'upload_image'
    image_form = UploadImageForm(initial={'action': action_upload_image})
    upload_url = '/challenges/%s/accept' % challenge_id
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == action_upload_image:
            if request.FILES:
                upload_form = UploadForm(request.POST, request.FILES)
                file = upload_form.save()
                participation.image = file
                participation.state = ChallengeParticipation.ACCEPTED_STATE
                participation.save()
            if request.is_ajax():
                return HttpResponse(redirect_url)
            return redirect(redirect_url)
        if request.is_ajax():
            return HttpResponse("%s|%s" % (
                blobstore.create_upload_url(upload_url),
                '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in image_form.errors.values()])))
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary,
        'image_form': image_form,
        'upload_url': blobstore.create_upload_url(upload_url),
        'redirect_url': redirect_url}
    return render(request, 'spudderspuds/challenges/pages/challenge_accept_upload.html', template_data)


def challenge_accept_state(request, participation_id):
    participation = get_object_or_404(ChallengeParticipation, id=participation_id)
    challenge = participation.challenge
    template = challenge.template
    template_data = {
        'challenge': challenge,
        'template': template,
        'participation': participation,
        'states': sorted([{'id': k, 'name': v} for k, v in STATES.items()], key=lambda x: x['id'])}
    return render(
        request,
        'spudderspuds/challenges/pages/challenge_accept_beneficiary_choose_state.html',
        template_data)


def challenge_accept_beneficiary(request, participation_id, state):
    participation = get_object_or_404(ChallengeParticipation, id=participation_id)
    if 'video_id' in request.GET:
        participation.youtube_video_id = request.GET['video_id']
        participation.state = ChallengeParticipation.ACCEPTED_STATE
        participation.save()
    challenge = participation.challenge
    template = challenge.template
    original_beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    clubs = _get_clubs_by_state(state)
    for club in clubs:
        club['is_original_beneficiary'] = (club['id'] == original_beneficiary.entity.id)
    clubs = sorted(clubs, key=lambda x: x['is_original_beneficiary'], reverse=True)
    template_data = {
        'challenge': challenge,
        'template': template,
        'participation': participation,
        'state': state,
        'clubs': clubs}
    return render(request, 'spudderspuds/challenges/pages/challenge_accept_beneficiary.html', template_data)


def challenge_accept_beneficiary_create_club(request, participation_id, state):
    participation = get_object_or_404(ChallengeParticipation, id=participation_id)
    challenge = participation.challenge
    template = challenge.template
    form = CreateTempClubForm()
    if request.method == 'POST':
        form = CreateTempClubForm(request.POST)
        if form.is_valid():
            temp_club = _create_temp_club(form, state)
            return redirect('/challenges/%s/beneficiary/%s/t/%s' % (participation_id, state, temp_club.id))
    template_data = {
        'form': form,
        'state': STATES[state],
        'template': template}
    return render(
        request,
        'spudderspuds/challenges/pages/challenge_accept_beneficiary_create_club.html',
        template_data)


def challenge_accept_beneficiary_set_donation(request, participation_id, state, club_id, club_class):
    club = get_object_or_404(club_class, id=club_id)
    participation = get_object_or_404(ChallengeParticipation, id=participation_id)
    challenge = participation.challenge
    template = challenge.template
    form = ChallengeConfigureForm({
        'donation_with_challenge': int(challenge.proposed_donation_amount),
        'donation_without_challenge': int(challenge.proposed_donation_amount_decline)})
    # if request.method == 'POST':
    #     form = ChallengeConfigureForm(request.POST)
    if form.is_valid():
        challenge = _create_challenge(
            club_class, club_id, form, request, template, challenge,
            youtube_video_id=participation.youtube_video_id, image=participation.image)
        return redirect('/challenges/%s/share' % challenge.id)
    template_data = {
        'club': club,
        'club_class': club_class.__name__,
        'form': form,
        'state': state,
        'template': template}
    return render(
        request,
        'spudderspuds/challenges/pages/challenge_accept_beneficiary_choose_donation.html',
        template_data)


def challenge_challenge(request):
    return render(request, 'spudderspuds/challenges/pages/challenge_challenge.html')


def challenge_challenge_accept_beneficiary(request, state=None):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s&message=challenge_challenge' % request.path)
    if not state:
        return redirect("%s%s" % (request.path, (request.current_role.state or 'no_state')))
    template_data = {
        'states': [{'id': '', 'name': 'Select a state ...'}] + sorted([
            {'id': k, 'name': v} for k, v in STATES.items()], key=lambda x: x['id'])}
    return render(request, 'spudderspuds/challenges/pages/challenge_challenge_accept_beneficiary.html', template_data)


def challenge_challenge_accept_beneficiary_load_clubs(request, state):
    template_data = {
        'state': STATES[state],
        'clubs': _get_clubs_by_state(state)}
    return render(request, 'spudderspuds/challenges/components/create_challenge_choose_club.html', template_data)


def challenge_challenge_accept_beneficiary_create_club(request, state):
    form = CreateTempClubForm()
    if request.method == 'POST':
        form = CreateTempClubForm(request.POST)
        if form.is_valid():
            temp_club = _create_temp_club(form, state)
            return redirect('/challenges/challenge_challenge/beneficiary/%s/clubs/t/%s' % (state, temp_club.id))
    template_data = {
        'form': form,
        'state': STATES[state]}
    return render(
        request,
        'spudderspuds/challenges/pages/challenge_challenge_accept_beneficiary_create_club.html',
        template_data)


def challenge_challenge_accept_notice(request, state=None, club_entity_type=None, club_id=None, participation_id=None):
    if state and club_entity_type and club_id:
        ccp = ChallengeChallengeParticipation(
            participating_entity_id=request.current_role.entity.id,
            participating_entity_type=request.current_role.entity_type,
            recipient_entity_id=club_id,
            recipient_entity_type=club_entity_type)
        ccp.save()
        return redirect('/challenges/challenge_challenge/%s/upload' % ccp.id)
    participation = get_object_or_404(ChallengeChallengeParticipation, id=participation_id)
    form = ChallengeChallengeParticipationForm()
    upload_url = '/challenges/challenge_challenge/%s/upload' % participation_id
    if request.method == 'POST':
        form = ChallengeChallengeParticipationForm(request.POST)
        if form.is_valid():
            participation.youtube_video_id = form.cleaned_data.get('youtube_video_id')
            participation.name = form.cleaned_data.get('challenge_name')
            participation.description = form.cleaned_data.get('challenge_description')
            participation.state = ChallengeChallengeParticipation.STATE_COMPLETE
            if request.FILES:
                file = UploadForm(request.POST, request.FILES).save()
                participation.image = file
            participation.save()
            redirect_url = '/challenges/challenge_challenge/%s/thanks?just_submitted=True' % participation_id
            if request.is_ajax():
                return HttpResponse(redirect_url)
            return redirect(redirect_url)
        if request.is_ajax():
            return HttpResponse("%s|%s" % (
                blobstore.create_upload_url(upload_url),
                '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
    template_data = {
        'form': form,
        'upload_url': blobstore.create_upload_url(upload_url)}
    return render(request, 'spudderspuds/challenges/pages/challenge_challenge_accept_upload.html', template_data)


def challenge_challenge_thanks(request, participation_id):
    participation = get_object_or_404(ChallengeChallengeParticipation, id=participation_id)
    creator = RoleController.GetRoleForEntityTypeAndID(
        participation.participating_entity_type,
        participation.participating_entity_id,
        RoleBase.EntityWrapperByEntityType(participation.participating_entity_type))
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        participation.recipient_entity_type,
        participation.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(participation.recipient_entity_type))
    template_data = {
        'participation': participation,
        'creator': creator,
        'beneficiary': beneficiary,
        'just_submitted': request.GET.get('just_submitted')}
    return render(request, 'spudderspuds/challenges/pages/challenge_challenge_thanks.html', template_data)


def tick(request):
    queue = taskqueue.Queue('challenges-sendemails')
    task = taskqueue.Task(url='/challenges/send_challenge_emails', method='GET')
    queue.add(task)
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


def send_challenge_emails(request):
    challenge_config = ChallengeServiceConfiguration.GetForSite()
    challenge_message_configs = ChallengeServiceMessageConfiguration.objects\
        .filter(configuration=challenge_config).order_by('-notify_after')

    active_templates = list(ChallengeTemplate.objects.filter(active=True))
    challenges = list(Challenge.objects.filter(template__in=active_templates))
    now = datetime.now()
    unexpired_challenges_dt = now - timedelta(minutes=challenge_config.time_to_complete)
    participations = list(ChallengeParticipation.objects.filter(
        challenge__in=challenges,
        state=ChallengeParticipation.PRE_ACCEPTED_STATE,
        created__gte=unexpired_challenges_dt
    ))

    if participations:
        exclude_ids = []
        for challenge_message_config in challenge_message_configs:
            notify_after = challenge_message_config.notify_after
            filtered_participations = [p for p in participations
                                       if (now - p.created).seconds / 60 >= notify_after and p.id not in exclude_ids]
            exclude_ids.extend(map(lambda p: p.id, filtered_participations))
            for participation in filtered_participations:
                extras = {
                    'challenge': participation.challenge,
                    'notify_after': notify_after,
                    'message': challenge_message_config.message
                }
                NotificationController.NotifyEntity(
                    participation.participating_entity_id,
                    participation.participating_entity_type,
                    Notification.COMPLETE_CHALLENGE_NOTIFICATION,
                    extras=extras)

    queue = taskqueue.Queue('challenges-sendemails')
    queue.purge()
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
