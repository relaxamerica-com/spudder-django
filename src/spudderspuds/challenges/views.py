import json
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from spudderaccounts.utils import change_current_role
from spudderaccounts.wrappers import RoleBase, RoleFan
from spudderdomain.controllers import RoleController, EntityController
from spudderdomain.models import Club, TempClub, FanPage, Challenge, ChallengeTemplate, ChallengeParticipation
from spudderdomain.wrappers import EntityBase
from spudderspuds.challenges.forms import CreateTempClubForm, ChallengeConfigureForm, ChallengesRegisterForm
from spudderspuds.challenges.forms import ChallengesSigninForm, AcceptChallengeForm
from spudderspuds.challenges.models import TempClubOtherInformation, ChallengeTree
from spudderspuds.utils import create_and_activate_fan_role
from spudmart.CERN.models import STATES
from spudmart.upload.forms import UploadForm
from google.appengine.api import blobstore


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
    temp_club, created = TempClub.objects.get_or_create(name=name, state=state)
    temp_club.email = email or temp_club.email
    temp_club.save()
    if other_info:
        temp_club_other_info, created = TempClubOtherInformation.objects.get_or_create(temp_club=temp_club)
        temp_club_other_info.other_information = other_info
        temp_club_other_info.save()
    return temp_club


def _create_challenge(club_class, club_id, form, request, template, parent=None, image=None, media=None):
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
    if parent or image:
        if parent:
            challenge.parent = parent
        if image:
            challenge.image = image
        if media:
            challenge.media = media
        challenge.save()
    if parent is None:
        ChallengeTree.CreateNewTree(challenge)
    else:
        ChallengeTree.AddChallengeToTree(challenge)
    return challenge


def clubs_splash(request):
    return render(request, 'spudderspuds/challenges/pages/splash_clubs.html')


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
        'spudderspuds/challenges/pages/create_signin.html',
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
            fan_page.save()
            login(request, authenticate(username=username, password=password))
            return redirect(form.cleaned_data.get('next', '/'))
    return render(
        request,
        'spudderspuds/challenges/pages/create_register.html',
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
        'spudderspuds/challenges/pages/create_challenge_choose_club.html',
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
        'spudderspuds/challenges/pages/create_challenge_choose_donation.html',
        template_data)


def challenge_share(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    template_data = {'challenge': challenge, 'template': template}
    return render(request, 'spudderspuds/challenges/pages/challenge_share.html', template_data)


def challenge_view(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    challenge_tree = ChallengeTree.GetChallengeTree(challenge).get_tree()
    challenge_tree_data = challenge_tree.to_dict()
    beneficiaries_data = challenge_tree.update_beneficiaries_data()
    template_data = {
        'challenge': challenge,
        'template': template,
        'challenge_tree': json.dumps(challenge_tree_data),
        'beneficiaries': beneficiaries_data,
        'owner': RoleController.GetRoleForEntityTypeAndID(
            challenge.creator_entity_type,
            challenge.creator_entity_id,
            RoleFan)}
    return render(request, 'spudderspuds/challenges/pages/challenge_view.html', template_data)


def challenge_accept(request, challenge_id):
    if not request.current_role or request.current_role.entity_type != RoleController.ENTITY_FAN:
        return redirect('/challenges/create/register?next=%s' % request.path)
    challenge = get_object_or_404(Challenge, id=challenge_id)
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    form = AcceptChallengeForm(initial={'donation': int(challenge.proposed_donation_amount)})
    upload_url = '/challenges/%s/accept' % challenge_id
    if request.method == 'POST':
        form = AcceptChallengeForm(request.POST)
        if form.is_valid():
            participation = ChallengeParticipation(
                challenge=challenge,
                participating_entity_id=request.current_role.entity.id,
                participating_entity_type=request.current_role.entity_type,
                donation_amount=form.cleaned_data.get('donation', 0),
                state=ChallengeParticipation.DONATE_ONLY_STATE)
            participation.save()

            if request.FILES:
                upload_form = UploadForm(request.POST, request.FILES)
                file = upload_form.save()
                participation.media = file
                participation.state = ChallengeParticipation.ACCEPTED_STATE
                participation.save()
            ChallengeTree.AddParticipationToTree(challenge, participation)
            redirect_url = '/challenges/%s/beneficiary/%s' % (participation.id, beneficiary.state)
            if request.is_ajax():
                return HttpResponse(redirect_url)
            return redirect(redirect_url)
        if request.is_ajax():
            return HttpResponse("%s|%s" % (
                blobstore.create_upload_url(upload_url),
                '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary,
        'form': form,
        'upload_url': blobstore.create_upload_url(upload_url)}
    return render(request, 'spudderspuds/challenges/pages/challenge_accept.html', template_data)


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
        'clubs': clubs
    }
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
            media=participation.media, image=participation.image)
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
