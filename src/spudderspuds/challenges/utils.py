from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from google.appengine.api import blobstore
from spudderaccounts.utils import change_current_role
from spudderadmin.templatetags.featuretags import feature_is_enabled
from spudderdomain.controllers import RoleController, EntityController, EventController
from spudderdomain.models import FanPage, Club, TempClub, Challenge, ChallengeTemplate, ChallengeParticipation
from spudderdomain.wrappers import EntityBase
from spudderspuds.challenges.forms import ChallengesSigninForm, ChallengesRegisterForm, UploadImageForm, AcceptChallengeForm
from spudderspuds.utils import create_and_activate_fan_role
from spudderstripe.utils import get_stripe_recipient_controller_for_club
from spudmart.upload.forms import UploadForm


class _AcceptAndPledgeEngineStates(object):
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


class TreeElement(object):
    parent_id = None

    def __init__(self, id, children={}, **kwargs):
        self.id = str(id)
        self.children = children
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def has_child(self, child):
        return child.id in self.children

    def add_child(self, child):
        self.children[child.id] = child

    def remove_child(self, child):
        self.children.pop(child)

    def to_dict(self):
        data = {self.id: self.__dict__.copy()}
        data[self.id]['children'] = []
        for child in self.children:
            data[self.id]['children'].append(self.children[child].to_dict())
        return data


class Tree(object):
    root = None

    def __init__(self, id, children={}, **kwargs):
        self.root = TreeElement(id, children, **kwargs)

    def add_element(self, element, parent_id):
        parent_id = str(parent_id)
        parent = self.find_element(parent_id)
        if parent is not None:
            parent.add_child(element)
            return True
        return False

    def remove_element(self, element):
        tree_element = self.find_element(element.id)
        if tree_element is not None:
            parent = self.find_element(tree_element.parent_id)
            parent.remove_child(element)
            return True
        return False

    def _find_element(self, element, element_id):
        if element_id in element.children:
            return element.children[element_id]
        else:
            for child_id, child in element.children.items():
                found_element = self._find_element(child, element_id)
                if found_element is not  None:
                    return found_element
        return None

    def find_element(self, element_id):
        element_id = str(element_id)
        if self.root.id == element_id:
            return self.root
        else:
            return self._find_element(self.root, element_id)

    def to_dict(self):
        return self.root.to_dict()


class ChallengeTreeHelper(Tree):
    beneficiaries = {}
    _participiants = {}

    def add_beneficiary(self, tree_element):
        recipient_entity_id = tree_element.recipient_entity_id
        recipient_entity_type = tree_element.recipient_entity_type
        if recipient_entity_id not in self.beneficiaries:
            self.beneficiaries[recipient_entity_id] = {
                'entity_id': recipient_entity_id,
                'entity_type': recipient_entity_type,
                'number_of_challenges': 0,
                'total_amount_raised': 0,
                'participants': [],
                'object': None
            }
        self.beneficiaries[recipient_entity_id]['number_of_challenges'] += 1
        for participation in tree_element.participations:
            self.beneficiaries[recipient_entity_id]['total_amount_raised'] += participation['donation_amount']
            participating_entity_id = str(participation['participating_entity_id'])
            participation_data = {
                'entity_id': participating_entity_id,
                'entity_type': participation['participating_entity_type']
            }
            if participation_data not in self.beneficiaries[recipient_entity_id]['participants']:
                self.beneficiaries[recipient_entity_id]['participants'].append(participation_data)
            self._participiants[participating_entity_id] = participation_data

    def __init__(self, id, children={}, **kwargs):
        self.beneficiaries = {}
        self._participiants = {}
        super(ChallengeTreeHelper, self).__init__(id, children, **kwargs)
        self.add_beneficiary(self.root)

    def add_element(self, element, parent_id):
        is_added = super(ChallengeTreeHelper, self).add_element(element, parent_id)
        if is_added:
            self.add_beneficiary(element)
        return is_added

    def update_beneficiaries_data(self):
        # get participiants objects
        # for now fans only
        fan_ids = [int(entity_id) for entity_id, data in self._participiants.items()
                   if data['entity_type'] == RoleController.ENTITY_FAN]
        fans = FanPage.objects.filter(id__in=fan_ids)
        for fan in fans:
            participating_entity_id = str(fan.id)
            self._participiants[participating_entity_id]['object'] = fan

        # get beneficiaries objects
        # for now clubs and temp clubs only
        club_ids = [int(entity_id) for entity_id, data in self.beneficiaries.items()
                    if data['entity_type'] == EntityController.ENTITY_CLUB]
        temp_club_ids = [int(entity_id) for entity_id, entity_type in self.beneficiaries.items()
                         if data['entity_type'] == EntityController.ENTITY_TEMP_CLUB]

        clubs = [c for c in Club.objects.filter(id__in=club_ids)]
        len(clubs)
        for club in clubs:
            club_id = str(club.id)
            self.beneficiaries[club_id]['object'] = club.__dict__
            for participiant_data in self.beneficiaries[club_id]['participants']:
                participating_entity_id = str(participiant_data['entity_id'])
                participiant_data['object'] = self._participiants[participating_entity_id]['object']

        temp_clubs = [tc for tc in TempClub.objects.filter(id__in=temp_club_ids)]
        len(temp_clubs)
        for temp_club in temp_clubs:
            temp_club_id = str(temp_club.id)
            self.beneficiaries[temp_club_id]['object'] = temp_club.__dict__
            for participiant_data in self.beneficiaries[temp_club_id]['participants']:
                participating_entity_id = str(participiant_data['entity_id'])
                participiant_data['object'] = self._participiants[participating_entity_id]['object']

        return self.beneficiaries


def get_affiliate_club_and_challenge(affiliate_key):
    if affiliate_key == "dreamsforkids":
        club_name = 'Dreams for Kids'
        challenge_template_slug = "piechallenge"
        challenge_name = "Pie Challenge"
        challenge_description = "Challenge your friends, family and fans to take a cream pie to the face!"
        challenge_you_tube_video_id = "vqgpHZ09St8"
        try:
            club = Club.objects.get(name=club_name)
        except Club.DoesNotExist:
            raise NotImplementedError('A club with the name %s does not exists.' % club_name)
        try:
            template = ChallengeTemplate.objects.get(slug=challenge_template_slug)
        except ChallengeTemplate.DoesNotExist:
            raise NotImplementedError("A challenge template with the slug %s does not exists, do you need to esnure "
                                      "challenge template in the admin console?" % challenge_template_slug)
        club_entity = EntityController.GetWrappedEntityByTypeAndId(
            EntityController.ENTITY_CLUB,
            club.id,
            EntityBase.EntityWrapperByEntityType(EntityController.ENTITY_CLUB))
        challenge, created = Challenge.objects.get_or_create(
            parent=None,
            template=template,
            name=challenge_name,
            creator_entity_id=club.id,
            creator_entity_type=EntityController.ENTITY_CLUB,
            recipient_entity_id=club.id,
            recipient_entity_type=EntityController.ENTITY_CLUB,
            proposed_donation_amount=10,
            proposed_donation_amount_decline=20)
        challenge.description = challenge_description
        challenge.youtube_video_id = challenge_you_tube_video_id
        challenge.save()
        return club_entity, challenge
    return None, None


def challenge_state_engine(request, challenge, engine, state):
    template_data = {
        'challenge': challenge,
        'state_engine': engine}
    if engine == "accept-and-pledge":
        if state == _AcceptAndPledgeEngineStates.LOGIN:
            if request.current_role:
                state = _AcceptAndPledgeEngineStates.NOTICE
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
                        state = _AcceptAndPledgeEngineStates.NOTICE
                template_data['form'] = form
                if state == _AcceptAndPledgeEngineStates.LOGIN:
                    return render(request, 'spudderspuds/challenges/pages_ajax/signin.html', template_data)
        if state == _AcceptAndPledgeEngineStates.REGISTER:
            if request.current_role:
                state = _AcceptAndPledgeEngineStates.NOTICE
            else:
                form = ChallengesRegisterForm(
                    initial=request.GET,
                    enable_register_club=False,
                    prevent_password_again=True)
                if request.method == "POST":
                    form = ChallengesRegisterForm(
                        request.POST,
                        enable_register_club=False,
                        prevent_password_again=True)
                    if form.is_valid():
                        username = form.cleaned_data.get('email_address')
                        password = form.cleaned_data.get('password')
                        user = User.objects.create_user(username, username, password)
                        user.save()
                        user.spudder_user.mark_password_as_done()
                        fan_entity = create_and_activate_fan_role(request, user)
                        request.current_role = fan_entity
                        fan_page = fan_entity.entity
                        fan_page.username = form.cleaned_data.get('username')
                        fan_page.state = form.cleaned_data.get('state')
                        fan_page.save()
                        login(request, authenticate(username=username, password=password))
                        if feature_is_enabled('tracking_pixels'):
                            EventController.RegisterEvent(request, EventController.CHALLENGER_USER_REGISTERER)
                        state = _AcceptAndPledgeEngineStates.NOTICE
                template_data['form'] = form
                if state == _AcceptAndPledgeEngineStates.REGISTER:
                    return render(request, 'spudderspuds/challenges/pages_ajax/register.html', template_data)
        if state == _AcceptAndPledgeEngineStates.NOTICE:
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
            return render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_notice.html', template_data)
        if state == _AcceptAndPledgeEngineStates.UPLOAD:
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
                        participation.save()
                        if feature_is_enabled('tracking_pixels'):
                            EventController.RegisterEvent(request, EventController.CHALLENGE_ACCEPTED)
                    if request.is_ajax():
                        return HttpResponse(redirect_url)
                    return redirect(redirect_url)
                if request.is_ajax():
                    return HttpResponse("%s|%s" % (
                        blobstore.create_upload_url(upload_url),
                        '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in image_form.errors.values()])))
            template_data['template'] = template
            template_data['beneficiary'] = beneficiary
            template_data['participation'] = participation
            template_data['redirect_url'] = redirect_url
            template_data['upload_url'] = blobstore.create_upload_url(upload_url)
            return render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_upload.html', template_data)
        if state == _AcceptAndPledgeEngineStates.UPLOAD_THANKS:
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
                participation.state_engine_state = _AcceptAndPledgeEngineStates.PLEDGE
                participation.save()
            template_data['template'] = template
            template_data['beneficiary'] = beneficiary
            template_data['participation'] = participation
            return render(
                request,
                'spudderspuds/challenges/pages_ajax/challenge_accept_upload_thanks.html',
                template_data)
        if state == _AcceptAndPledgeEngineStates.SHARE:
            template = challenge.template
            beneficiary = EntityController.GetWrappedEntityByTypeAndId(
                challenge.recipient_entity_type,
                challenge.recipient_entity_id,
                EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
            template_data['template'] = template
            template_data['beneficiary'] = beneficiary
            return render(
                request,
                'spudderspuds/challenges/pages_ajax/challenge_accept_share.html',
                template_data)
        if state == _AcceptAndPledgeEngineStates.PLEDGE:
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
                    participation.state_engine_state = _AcceptAndPledgeEngineStates.PLEDGE_THANKS
                    beneficiary_can_receive_donations = False
                    if beneficiary.entity_type == EntityController.ENTITY_CLUB:
                        if beneficiary.entity.is_fully_activated():
                            beneficiary_can_receive_donations = True
                    if beneficiary_can_receive_donations and participation.donation_amount > 0:
                        participation.state = ChallengeParticipation.AWAITING_PAYMENT
                    participation.save()
                    if feature_is_enabled('challenge_tree'):
                        from spudderspuds.challenges.models import ChallengeTree
                        ChallengeTree.AddParticipationToTree(challenge, participation)
                    redirect_url = '/challenges/%s/%s/%s' % (
                        challenge.id,
                        engine,
                        _AcceptAndPledgeEngineStates.PLEDGE_THANKS)
                    if participation.state == ChallengeParticipation.AWAITING_PAYMENT:
                        redirect_url.replace(
                            _AcceptAndPledgeEngineStates.PLEDGE_THANKS,
                            _AcceptAndPledgeEngineStates.PAY)
                        participation.state_engine_state = _AcceptAndPledgeEngineStates.PAY
                        participation.save()
                    if request.is_ajax():
                        return HttpResponse(redirect_url)
                    return redirect(redirect_url)
                if request.is_ajax():
                    return HttpResponse("%s|%s" % (
                        request.path,
                        '<br/>'.join(['<br/>'.join([_e for _e in e]) for e in form.errors.values()])))
            template_data = {
                'challenge': challenge,
                'template': template,
                'beneficiary': beneficiary,
                'form': form}
            return render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pledge.html', template_data)
        if state == _AcceptAndPledgeEngineStates.PLEDGE_THANKS:
            template = challenge.template
            beneficiary = EntityController.GetWrappedEntityByTypeAndId(
                challenge.recipient_entity_type,
                challenge.recipient_entity_id,
                EntityBase.EntityWrapperByEntityType(challenge.recipient_entity_type))
            template_data = {
                'challenge': challenge,
                'template': template,
                'beneficiary': beneficiary}
            return render(
                request,
                'spudderspuds/challenges/pages_ajax/challenge_accept_pledge_thanks.html',
                template_data)
        if state == _AcceptAndPledgeEngineStates.PAY:
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
                participation.state_engine_state = _AcceptAndPledgeEngineStates.PLEDGE_THANKS
                participation.save()
                return redirect('/challenges/%s/%s/%s' % (
                    challenge.id,
                    engine,
                    _AcceptAndPledgeEngineStates.PLEDGE_THANKS))
            if request.method == "POST":
                token = request.POST.get('stripeToken')
                stripe_controller = get_stripe_recipient_controller_for_club(beneficiary.entity)
                donation = int(participation.donation_amount) * 100
                payment_made = stripe_controller.accept_payment(
                    "Donation of $%s by %s to %s for %s" % (
                        donation,
                        request.user.email,
                        beneficiary.name,
                        challenge.name),
                    token,
                    donation)
                if payment_made:
                    participation.state_engine_state = _AcceptAndPledgeEngineStates.PAY_THANKS
                    participation.donation_amount = donation
                    participation.save()
                return redirect('/challenges/%s/%s' % (challenge.id, engine))
            template_data = {
                'challenge': challenge,
                'participation': participation,
                'template': template,
                'beneficiary': beneficiary,
                'errors': request.method == 'POST'}
            return render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pay.html', template_data)
        if state == _AcceptAndPledgeEngineStates.PAY_THANKS:
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
            return render(request, 'spudderspuds/challenges/pages_ajax/challenge_accept_pay_thanks.html', template_data)





