import json
import logging
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from google.appengine.api import blobstore
from spudderaccounts.utils import change_current_role, create_at_name_from_email_address
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderdomain.controllers import RoleController, EntityController, EventController
from spudderdomain.models import FanPage, Club, TempClub, Challenge, ChallengeTemplate, ChallengeParticipation, _ChallengeTree, _ChallengeTreeChallenge
from spudderdomain.wrappers import EntityBase
from spudderspuds.challenges.forms import ChallengesSigninForm, ChallengesRegisterForm, UploadImageForm, AcceptChallengeForm, CreateTempClubForm
from spudderspuds.forms import FanRegisterForm
from spudderspuds.utils import create_and_activate_fan_role
from spudderstripe.utils import get_stripe_recipient_controller_for_club
from spudmart.upload.forms import UploadForm


class _StateEngineStates(object):
    LOGIN = '0'
    REGISTER = '1'
    NOTICE = '2'
    UPLOAD = '3'
    UPLOAD_THANKS = '4'
    CHOOSE_TEAM = '5'
    CREATE_TEAM = '6'
    SHARE = '7'
    PLEDGE = '8'
    PLEDGE_THANKS = '9'
    PAY = '10'
    PAY_THANKS = '11'
    PAY_FAILED = '12'


def extract_statistics_from_challenge_tree(challenge_tree):
    stats = {
        'root_challenge': None,
        'all_participations': []}

    # Loop through the ctc's
    for ctc in _ChallengeTreeChallenge.objects.filter(challenge_tree=challenge_tree):
        challenge_dict = json.loads(ctc.challenge_json)

        # If this one has no parent then its the root
        if not challenge_dict.get('parent'):
            stats['root_challenge'] = Challenge.objects.get(id=ctc.challenge_id)

        for participation in challenge_dict.get('participations'):
            stats['all_participations'].append(participation)

    stats['all_participations'] = sorted(stats['all_participations'], key=lambda p: p.get('created'), reverse=True)

    return stats


def get_affiliate_club_and_challenge(affiliate_key):
    if affiliate_key == "dreamsforkids-piechallenge":
        if not feature_is_enabled('challenge_dreamsforkids_piechallenge'):
            raise Http404
        club_name = 'Dreams for Kids'
        challenge_template_slug = "piechallenge"
        challenge_you_tube_video_id = "vqgpHZ09St8"
    elif affiliate_key == "dreamsforkids-payitforward":
        if not feature_is_enabled('challenge_dreamsforkids_payitforward'):
            raise Http404
        club_name = "Dreams for Kids"
        challenge_template_slug = "payitforward"
        challenge_you_tube_video_id = "R_EkUOThl7w"
    elif affiliate_key == "bpt_memorial_field_fund_rak":
        if not feature_is_enabled('challenge_bpt_memorial_field_fund_rak'):
            raise Http404
        club_name = "Brendan P. Tevlin FUND"
        challenge_template_slug = "bptrak"
        challenge_you_tube_video_id = "R2yX64Gh2iI"
    else:
        return None, None

    try:
        club = Club.objects.get(name=club_name)
    except Club.DoesNotExist:
        raise NotImplementedError('A club with the name %s does not exists.' % club_name)
    try:
        template = ChallengeTemplate.objects.get(slug=challenge_template_slug)
    except ChallengeTemplate.DoesNotExist:
        raise NotImplementedError("A challenge template with the slug %s does not exists, do you need to ensure "
                                  "challenge template in the admin console?" % challenge_template_slug)
    club_entity = EntityController.GetWrappedEntityByTypeAndId(
        EntityController.ENTITY_CLUB,
        club.id,
        EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_CLUB))
    challenge, created = Challenge.objects.get_or_create(
        parent=None,
        template=template,
        name=template.name,
        creator_entity_id=club.id,
        creator_entity_type=EntityController.ENTITY_CLUB,
        recipient_entity_id=club.id,
        recipient_entity_type=EntityController.ENTITY_CLUB,
        proposed_donation_amount=10,
        proposed_donation_amount_decline=20)
    challenge.description = template.description
    challenge.youtube_video_id = challenge_you_tube_video_id
    challenge.save()
    return club_entity, challenge


def challenge_state_engine(request, challenge, engine, state):
    template_data = {
        'challenge': challenge,
        'state_engine': engine}
    if state == _StateEngineStates.LOGIN:
        response, state = _state_engine_process_login(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.REGISTER:
        response, state = _state_engine_process_register(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.NOTICE:
        response, state = _state_engine_process_notice(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.UPLOAD:
        response, state = _state_engine_process_upload(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.UPLOAD_THANKS:
        response, state = _state_engine_process_upload_thanks(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.CREATE_TEAM:
        response, state = _state_engine_process_create_team(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.SHARE:
        response, state = _state_engine_process_share(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.PLEDGE:
        response, state = _state_engine_process_pledge(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.PLEDGE_THANKS:
        response, state = _state_engine_process_pledge_thanks(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.PAY:
        response, state = _state_engine_process_pay(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.PAY_THANKS:
        response, state = _state_engine_process_pay_thanks(request, challenge, engine, state, template_data)
        if response:
            return response
    if state == _StateEngineStates.PAY_FAILED:
        response, state = _state_engine_process_pay_failed(request, challenge, engine, state, template_data)
        if response:
            return response


def _state_engine_process_login(request, challenge, engine, state, template_data):
    response = None
    next_state = _StateEngineStates.NOTICE
    if engine == "pledge-only":
        next_state = _StateEngineStates.PLEDGE
    if request.current_role:
        state = next_state
    else:
        form = ChallengesSigninForm(initial=request.GET)
        if request.method == "POST":
            form = ChallengesSigninForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('email_address')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                login(request, user)
                request.current_role = change_current_role(request)
                state = next_state
                response = redirect('/challenges/%s/%s/%s' % (challenge.id, engine, state))
        template_data['form'] = form
        if state == _StateEngineStates.LOGIN:
            response = render(request, 'spudderspuds/challenges/pages_ajax/signin.html', template_data)
    return response, state


def _state_engine_process_register(request, challenge, engine, state, template_data):
    response = None
    next_state = _StateEngineStates.NOTICE
    if engine == "pledge-only":
        next_state = _StateEngineStates.PLEDGE
    if request.current_role:
        state = next_state
    else:
        form = FanRegisterForm()
        if request.method == "POST":
            form = FanRegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('email_address')
                password = form.cleaned_data.get('password')
                user = User.objects.create_user(username, username, password)
                user.save()
                user.spudder_user.mark_password_as_done()
                fan_entity = create_and_activate_fan_role(request, user)
                request.current_role = fan_entity
                fan_page = fan_entity.entity
                fan_page.username = create_at_name_from_email_address(username)
                fan_page.state = form.cleaned_data.get('state')
                fan_page.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                if feature_is_enabled('tracking_pixels'):
                    EventController.RegisterEvent(request, EventController.CHALLENGER_USER_REGISTERER)
                state = next_state
                response = redirect('/challenges/%s/%s/%s' % (challenge.id, engine, state))
        if state == _StateEngineStates.REGISTER:
            template_data['form'] = form
            response = render(request, 'spudderspuds/challenges/pages_ajax/register.html', template_data)
    return response, state


def _state_engine_process_notice(request, challenge, engine, state, template_data):
    response = None
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
    participation.state_engine = engine
    participation.state_engine_state = state
    participation.save()
    template_data['template'] = template
    template_data['beneficiary'] = beneficiary
    template_data['participation'] = participation
    response = render(
        request,
        'spudderspuds/challenges/pages_ajax/challenge_accept_notice.html',
        template_data)
    return response, state


def _state_engine_process_upload(request, challenge, engine, state, template_data):
    response = None
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation = ChallengeParticipation.objects.get(
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    redirect_url = '/challenges/%s/%s/4?just_pledged=True' % (challenge.id, engine)
    action_upload_image = 'upload_image'
    image_form = UploadImageForm(initial={'action': action_upload_image})
    upload_url = '/challenges/%s/accept' % challenge.id
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == action_upload_image:
            if request.FILES:
                upload_form = UploadForm(request.POST, request.FILES)
                file = upload_form.save()
                participation.image = file
                participation.state = ChallengeParticipation.ACCEPTED_STATE
                participation.state_engine = engine
                participation.save()
                if feature_is_enabled('tracking_pixels'):
                    EventController.RegisterEvent(request, EventController.CHALLENGE_ACCEPTED)
            if request.is_ajax():
                response = HttpResponse(redirect_url)
                return response, state
            response = redirect(redirect_url)
            return response, state
        if request.is_ajax():
            response = HttpResponse("%s|%s" % (blobstore.create_upload_url(upload_url), '<br/>'.join(
                ['<br/>'.join([_e for _e in e]) for e in image_form.errors.values()])))
            return response, state
    template_data['template'] = template
    template_data['beneficiary'] = beneficiary
    template_data['participation'] = participation
    template_data['redirect_url'] = redirect_url
    template_data['upload_url'] = blobstore.create_upload_url(upload_url)
    response = render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_upload.html', template_data)
    return response, state


def _state_engine_process_upload_thanks(request, challenge, engine, state, template_data):
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation = ChallengeParticipation.objects.get(
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    if request.GET.get('video_id'):
        participation.youtube_video_id = request.GET['video_id']
        participation.state_engine_state = state
        participation.state_engine = engine
        participation.save()
        challenge = Challenge(
            template=template,
            name=template.name,
            parent=challenge,
            description=challenge.description,
            creator_entity_id=request.current_role.entity.id,
            creator_entity_type=request.current_role.entity_type,
            recipient_entity_id=challenge.recipient_entity_id,
            recipient_entity_type=challenge.recipient_entity_type,
            proposed_donation_amount=challenge.proposed_donation_amount,
            proposed_donation_amount_decline=challenge.proposed_donation_amount_decline,
            creating_participant=participation,
            youtube_video_id=participation.youtube_video_id)
        challenge.save()
        template_data['challenge'] = challenge
        template_data['just_uploaded'] = True
        participation.state_engine_state = _StateEngineStates.PLEDGE
        participation.state_engine = engine
        participation.save()
    template_data['template'] = template
    template_data['beneficiary'] = beneficiary
    template_data['participation'] = participation
    response = render(
        request,
        'spudderspuds/challenges/pages_ajax/challenge_accept_upload_thanks.html',
        template_data)
    return response, state


def _state_engine_process_create_team(request, challenge, engine, state, template_data):
    response = None
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    template_data['beneficiary'] = beneficiary
    form = CreateTempClubForm()
    if request.POST:
        form = CreateTempClubForm(request.POST)
        if form.is_valid():
            temp_club = _create_temp_club(form, request.current_role.state)
            challenge.recipient_entity_id = temp_club.id
            challenge.recipient_entity_type = EntityController.ENTITY_TEMP_CLUB
            challenge.save()
            state = _StateEngineStates.SHARE
        elif request.is_ajax():
            response = HttpResponse("%s|%s" % (
                request.path, '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
    if state == _StateEngineStates.CREATE_TEAM:
        template_data['form'] = form
        response = render(
            request,
            'spudderspuds/challenges/pages_ajax/challenge_accept_beneficiary_create_club.html',
            template_data)
    return response, state


def _state_engine_process_pledge(request, challenge, engine, state, template_data):
    response = None
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation, created = ChallengeParticipation.objects.get_or_create(
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    participation.state_engine_state = _StateEngineStates.PLEDGE
    participation.save()
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
            participation.state_engine_state = _StateEngineStates.PLEDGE_THANKS
            beneficiary_can_receive_donations = False
            if beneficiary.entity_type == EntityController.ENTITY_CLUB:
                if beneficiary.entity.is_fully_activated():
                    beneficiary_can_receive_donations = True
            if beneficiary_can_receive_donations and participation.donation_amount > 0:
                participation.state = ChallengeParticipation.AWAITING_PAYMENT
            participation.state_engine = engine
            participation.save()
            redirect_url = '/challenges/%s/%s/%s' % (
                challenge.id,
                engine,
                _StateEngineStates.PLEDGE_THANKS)
            if participation.state == ChallengeParticipation.AWAITING_PAYMENT:
                redirect_url = '/challenges/%s/%s/%s' % (
                    challenge.id,
                    engine,
                    _StateEngineStates.PAY)
                participation.state_engine_state = _StateEngineStates.PAY
                participation.state_engine = engine
                participation.save()
            response = redirect(redirect_url)
            return response, state
        if request.is_ajax():
            response = HttpResponse("%s|%s" % (
                request.path,
                '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
            return response, state
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary,
        'form': form}
    response = render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pledge.html', template_data)
    return response, state


def _state_engine_process_share(request, challenge, engine, state, template_data):
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    template_data['template'] = template
    template_data['beneficiary'] = beneficiary
    response = render(
        request,
        'spudderspuds/challenges/pages_ajax/challenge_accept_share.html',
        template_data)
    return response, state


def _state_engine_process_pledge_thanks(request, challenge, engine, state, template_data):
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    template_data = {
        'challenge': challenge,
        'template': template,
        'beneficiary': beneficiary}
    response = render(
        request,
        'spudderspuds/challenges/pages_ajax/challenge_accept_pledge_thanks.html',
        template_data)
    return response, state


def _state_engine_process_pay(request, challenge, engine, state, template_data):
    template = challenge.template
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    participation = get_object_or_404(
        ChallengeParticipation,
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    if beneficiary.entity_type != EntityController.ENTITY_CLUB or not beneficiary.entity.is_fully_activated():
        participation.state_engine_state = _StateEngineStates.PLEDGE_THANKS
        participation.state_engine = engine
        participation.save()
        response = redirect('/challenges/%s/%s/%s' % (
            challenge.id,
            engine,
            _StateEngineStates.PLEDGE_THANKS))
        return response, state

    if request.method == "POST":
        token = request.POST.get('stripeToken', None)
        if token is None:
            logging.error('Missing stripeToken in payment processing')
            return None, _StateEngineStates.PAY_FAILED

        stripe_controller = get_stripe_recipient_controller_for_club(beneficiary.entity)
        if stripe_controller is None:
            return None, _StateEngineStates.PAY_FAILED

        donation = int(participation.donation_amount) * 100
        payment_status = stripe_controller.accept_payment(
            "Donation of $%s by %s to %s for %s" % (
                int(participation.donation_amount),
                request.user.email,
                beneficiary.name,
                challenge.name),
            token,
            donation)
        if not payment_status['success']:
            return None, _StateEngineStates.PAY_FAILED

        participation.state_engine_state = _StateEngineStates.PAY_THANKS
        participation.charge_id = payment_status['charge_id']
        participation.save()

        response = redirect('/challenges/%s/%s' % (challenge.id, engine))

        return response, state

    template_data = {
        'challenge': challenge,
        'participation': participation,
        'template': template,
        'beneficiary': beneficiary,
        'errors': request.method == 'POST'}
    response = render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pay.html', template_data)
    return response, state


def _state_engine_process_pay_thanks(request, challenge, engine, state, template_data):
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    template = challenge.template
    participation = get_object_or_404(
        ChallengeParticipation,
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)
    template_data = {
        'challenge': challenge,
        'participation': participation,
        'template': template,
        'beneficiary': beneficiary}
    response = render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pay_thanks.html', template_data)
    return response, state


def _state_engine_process_pay_failed(request, challenge, engine, state, template_data):
    beneficiary = EntityController.GetWrappedEntityByTypeAndId(
        challenge.recipient_entity_type,
        challenge.recipient_entity_id,
        EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
    template = challenge.template
    participation = get_object_or_404(
        ChallengeParticipation,
        challenge=challenge,
        participating_entity_id=request.current_role.entity.id,
        participating_entity_type=request.current_role.entity_type)

    participation.state_engine_state = _StateEngineStates.PAY_FAILED
    participation.save()

    if request.method == "POST":
        response = redirect('/challenges/%s/%s' % (challenge.id, engine))
    else:
        template_data = {
            'challenge': challenge,
            'participation': participation,
            'template': template,
            'beneficiary': beneficiary}
        response = render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pay_failed.html', template_data)

    return response, state


def _create_temp_club(form, state):
    name = form.cleaned_data['name'].upper()
    email = form.cleaned_data['email']
    website = form.cleaned_data['website']
    contact_number = form.cleaned_data['contact_number']
    temp_club, created = TempClub.objects.get_or_create(name=name, state=state)
    temp_club.email = email or temp_club.email
    temp_club.save()
    if website or contact_number:
        from spudderspuds.challenges.models import TempClubOtherInformation
        temp_club_other_info, created = TempClubOtherInformation.objects.get_or_create(temp_club=temp_club)
        temp_club_other_info.website = website
        temp_club_other_info.contact_number = contact_number
        temp_club_other_info.save()
    return temp_club


# class TreeElement(object):
#     parent_id = None
#
#     def __init__(self, id, children={}, **kwargs):
#         self.id = str(id)
#         self.children = children
#         for key in kwargs:
#             setattr(self, key, kwargs[key])
#
#     def has_child(self, child):
#         return child.id in self.children
#
#     def add_child(self, child):
#         self.children[child.id] = child
#
#     def remove_child(self, child):
#         self.children.pop(child)
#
#     def to_dict(self):
#         data = {self.id: self.__dict__.copy()}
#         data[self.id]['children'] = []
#         for child in self.children:
#             data[self.id]['children'].append(self.children[child].to_dict())
#         return data
#
#
# class Tree(object):
#     root = None
#
#     def __init__(self, id, children={}, **kwargs):
#         self.root = TreeElement(id, children, **kwargs)
#
#     def add_element(self, element, parent_id):
#         parent_id = str(parent_id)
#         parent = self.find_element(parent_id)
#         if parent is not None:
#             parent.add_child(element)
#             return True
#         return False
#
#     def remove_element(self, element):
#         tree_element = self.find_element(element.id)
#         if tree_element is not None:
#             parent = self.find_element(tree_element.parent_id)
#             parent.remove_child(element)
#             return True
#         return False
#
#     def _find_element(self, element, element_id):
#         if element_id in element.children:
#             return element.children[element_id]
#         else:
#             for child_id, child in element.children.items():
#                 found_element = self._find_element(child, element_id)
#                 if found_element is not  None:
#                     return found_element
#         return None
#
#     def find_element(self, element_id):
#         element_id = str(element_id)
#         if self.root.id == element_id:
#             return self.root
#         else:
#             return self._find_element(self.root, element_id)
#
#     def to_dict(self):
#         return self.root.to_dict()
#
#
# class ChallengeTreeHelper(Tree):
#     beneficiaries = {}
#     _participiants = {}
#
#     def add_beneficiary(self, tree_element):
#         recipient_entity_id = tree_element.recipient_entity_id
#         recipient_entity_type = tree_element.recipient_entity_type
#         if recipient_entity_id not in self.beneficiaries:
#             self.beneficiaries[recipient_entity_id] = {
#                 'entity_id': recipient_entity_id,
#                 'entity_type': recipient_entity_type,
#                 'number_of_challenges': 0,
#                 'total_amount_raised': 0,
#                 'participants': [],
#                 'object': None
#             }
#         self.beneficiaries[recipient_entity_id]['number_of_challenges'] += 1
#         for participation in tree_element.participations:
#             self.beneficiaries[recipient_entity_id]['total_amount_raised'] += participation['donation_amount']
#             participating_entity_id = str(participation['participating_entity_id'])
#             participation_data = {
#                 'entity_id': participating_entity_id,
#                 'entity_type': participation['participating_entity_type']
#             }
#             if participation_data not in self.beneficiaries[recipient_entity_id]['participants']:
#                 self.beneficiaries[recipient_entity_id]['participants'].append(participation_data)
#             self._participiants[participating_entity_id] = participation_data
#
#     def __init__(self, id, children={}, **kwargs):
#         self.beneficiaries = {}
#         self._participiants = {}
#         super(ChallengeTreeHelper, self).__init__(id, children, **kwargs)
#         self.add_beneficiary(self.root)
#
#     def add_element(self, element, parent_id):
#         is_added = super(ChallengeTreeHelper, self).add_element(element, parent_id)
#         if is_added:
#             self.add_beneficiary(element)
#         return is_added
#
#     def update_beneficiaries_data(self):
#         # get participiants objects
#         # for now fans only
#         fan_ids = [int(entity_id) for entity_id, data in self._participiants.items()
#                    if data['entity_type'] == RoleController.ENTITY_FAN]
#         fans = FanPage.objects.filter(id__in=fan_ids)
#         for fan in fans:
#             participating_entity_id = str(fan.id)
#             self._participiants[participating_entity_id]['object'] = fan
#
#         # get beneficiaries objects
#         # for now clubs and temp clubs only
#         club_ids = [int(entity_id) for entity_id, data in self.beneficiaries.items()
#                     if data['entity_type'] == EntityController.ENTITY_CLUB]
#         temp_club_ids = [int(entity_id) for entity_id, entity_type in self.beneficiaries.items()
#                          if data['entity_type'] == EntityController.ENTITY_TEMP_CLUB]
#
#         clubs = [c for c in Club.objects.filter(id__in=club_ids)]
#         len(clubs)
#         for club in clubs:
#             club_id = str(club.id)
#             self.beneficiaries[club_id]['object'] = club.__dict__
#             for participiant_data in self.beneficiaries[club_id]['participants']:
#                 participating_entity_id = str(participiant_data['entity_id'])
#                 participiant_data['object'] = self._participiants[participating_entity_id]['object']
#
#         temp_clubs = [tc for tc in TempClub.objects.filter(id__in=temp_club_ids)]
#         len(temp_clubs)
#         for temp_club in temp_clubs:
#             temp_club_id = str(temp_club.id)
#             self.beneficiaries[temp_club_id]['object'] = temp_club.__dict__
#             for participiant_data in self.beneficiaries[temp_club_id]['participants']:
#                 participating_entity_id = str(participiant_data['entity_id'])
#                 participiant_data['object'] = self._participiants[participating_entity_id]['object']
#
#         return self.beneficiaries
