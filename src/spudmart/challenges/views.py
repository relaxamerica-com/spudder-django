from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from google.appengine.api import blobstore
from spudderdomain.forms import NewChallengeTemplateForm, ChallengeClubForm, ChallengeDonationForm,\
    ChallengeDetailsForm, ChooseChallengeTemplateForm, EditChallengeTemplateForm, DeclineChallengeForm, \
    DonateChallengeForm, AcceptChallengeForm
from spudderdomain.models import ChallengeTemplate, Club, Challenge, ChallengeParticipation
from spudmart.upload.forms import UploadForm


def get_challenges(request):
    challenges = Challenge.objects.select_related('template').order_by('-created')
    template_data = {'challenges': challenges}
    return render(request, 'spudderspuds/challenges/pages/challenges.html', template_data)


def view_challenge(request, challenge_id):
    try:
        challenge = Challenge.objects.select_related('template__image').get(id=challenge_id)
    except Challenge.DoesNotExist:
        return HttpResponseNotFound()

    is_creator = False
    if request.current_role is not None and challenge.creator_entity_id == str(request.current_role.entity.id) \
            and challenge.creator_entity_type == request.current_role.entity_type:
        is_creator = True

    template_data = {
        'challenge': challenge,
        'is_creator': is_creator
    }
    return render(request, 'spudderspuds/challenges/pages/view_challenge.html', template_data)


def view_challenge_template(request, template_id):
    try:
        template = ChallengeTemplate.objects.get(id=template_id)
    except ChallengeTemplate.DoesNotExist:
        return HttpResponseNotFound()

    challenges = Challenge.objects.filter(template=template).order_by('-created')[:5]
    template_data = {
        'template': template,
        'challenges': challenges
    }
    return render(request, 'spudderspuds/challenges/pages/view_template.html', template_data)


def edit_challenge_template(request, template_id):
    try:
        template = ChallengeTemplate.objects.get(id=template_id)
    except ChallengeTemplate.DoesNotExist:
        return HttpResponseNotFound()

    form = EditChallengeTemplateForm(initial=template.__dict__, image=template.image)

    if request.method == 'POST':
        form = EditChallengeTemplateForm(request.POST, template_id=template.id, image=template.image)

        if form.is_valid():
            data = form.cleaned_data
            template.name = data.get('name')
            template.description = data.get('description')

            upload_form = UploadForm(request.POST, request.FILES)
            if upload_form.is_valid():
                template.image = upload_form.save()
            template.save()
            return HttpResponseRedirect('/challenges/template/%s' % template.id)
    template_data = {
        'template': template,
        'form': form,
        'upload_url': blobstore.create_upload_url('/challenges/template/%s/edit' % template.id)
    }
    return render(request, 'spudderspuds/challenges/pages/edit_template.html', template_data)


def new_challenge_wizard_view(request):
    if request.user.is_authenticated():
        wizard = NewChallengeWizard()
        return wizard(request)
    else:
        request.session['redirect_after_auth'] = '/challenges/create'
        return HttpResponseRedirect('/spuds/register')


def accept_challenge_wizard(request, challenge_id):
    try:
        challenge = Challenge.objects.select_related('template__image').get(id=challenge_id)
    except Challenge.DoesNotExist:
        return HttpResponseNotFound()

    if request.user.is_authenticated():
        wizard = AcceptChallengeWizard(AcceptChallengeWizard.FORMS_LIST, challenge=challenge)
        return wizard(request)
    else:
        request.session['redirect_after_auth'] = '/challenges/%s/accept' % challenge_id
        return HttpResponseRedirect('/spuds/register')


def donate_challenge(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        return HttpResponseNotFound()

    if not request.user.is_authenticated():
        request.session['redirect_after_auth'] = '/challenges/%s/donate' % challenge_id
        return HttpResponseRedirect('/spuds/register')

    form = DonateChallengeForm()
    if request.method == 'POST':
        form = DonateChallengeForm(request.POST)
        if form.is_valid():
            donation_amount = form.cleaned_data.get('donation_amount')
            participation = ChallengeParticipation(
                challenge=challenge,
                participating_entity_id=request.current_role.entity.id,
                participating_entity_type=request.current_role.entity_type,
                state=ChallengeParticipation.DONATE_ONLY_STATE,
                donation_amount=donation_amount
            )
            participation.save()
            return HttpResponseRedirect('/challenges/%s' % challenge.id)

    template_data = {
        'challenge': challenge,
        'form': form
    }
    return render(request, 'spudderspuds/challenges/pages/donate_challenge.html', template_data)


def decline_challenge(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        return HttpResponseNotFound()

    if not request.user.is_authenticated():
        request.session['redirect_after_auth'] = '/challenges/%s/decline' % challenge_id
        return HttpResponseRedirect('/spuds/register')

    form = DeclineChallengeForm()
    if request.method == 'POST':
        form = DeclineChallengeForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get('message', '')
            participation = ChallengeParticipation(
                challenge=challenge,
                participating_entity_id=request.current_role.entity.id,
                participating_entity_type=request.current_role.entity_type,
                state=ChallengeParticipation.DECLINED_STATE,
                message=message
            )
            participation.save()
            return HttpResponseRedirect('/challenges/%s' % challenge.id)

    template_data = {
        'challenge': challenge,
        'form': form
    }
    return render(request, 'spudderspuds/challenges/pages/decline_challenge.html', template_data)


class NewChallengeWizard(FormWizard):
    TEMPLATES = [
        "spudderspuds/challenges/wizards/create_challenge/choose_challenge_template.html",
        "spudderspuds/challenges/wizards/create_challenge/new_challenge_template.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_club.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_donation.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_details.html"
    ]
    FORMS_LIST = [
        ChooseChallengeTemplateForm, NewChallengeTemplateForm,
        ChallengeClubForm, ChallengeDonationForm, ChallengeDetailsForm
    ]
    STEPS = ['choose_template', 'create_template', 'choose_club', 'set_donation_amount', 'update_details']

    def __init__(self, *args, **kwargs):
        super(NewChallengeWizard, self).__init__(form_list=self.FORMS_LIST[:], *args, **kwargs)
        self.templates = self.TEMPLATES[:]
        self.steps = self.STEPS[:]
        self.challenge_template = None
        for index in xrange(self.num_steps()):
            self.initial[index] = {}
        self.extra_context = self.update_extra_context(self.extra_context)

    def get_template(self, step):
        return [self.templates[step]]

    def remove_step(self, step):
        self.form_list.pop(step)
        self.templates.pop(step)
        self.steps.pop(step)
        self.initial.pop(step)

    def update_initial(self, step, dictionary):
        self.initial[step].update(dictionary)

    def update_extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        templates = ChallengeTemplate.objects.all()
        clubs = Club.objects.all()
        extra_context.update({
            'templates': templates,
            'clubs': clubs
        })
        return extra_context

    def process_step(self, request, form, step):
        if self.steps[step] == 'choose_template':
            template_id = form.cleaned_data.get('template_id')
            if template_id:
                # remove next step and last step
                self.remove_step(step + 1)
                self.remove_step(self.num_steps() - 1)
                # set initial form value for last step
                template = get_object_or_404(ChallengeTemplate, id=int(template_id))
                self.challenge_template = template
        elif self.steps[step] == 'create_template':
            self.update_initial(self.num_steps() - 1, form.cleaned_data)

    def done(self, request, form_list):
        challenge = Challenge(
            creator_entity_id=request.current_role.entity.id,
            creator_entity_type=request.current_role.entity_type,
            recipient_entity_id=request.current_role.entity.id,
            recipient_entity_type=request.current_role.entity_type
        )
        for index, form in enumerate(form_list):
            step_name = self.steps[index]
            if step_name == 'choose_template' and self.challenge_template:
                challenge.template = self.challenge_template
                challenge.name = self.challenge_template.name
                challenge.description = self.challenge_template.description
            elif step_name == 'create_template' and not self.challenge_template:
                challenge_template = ChallengeTemplate(
                    name=form.cleaned_data.get('name'),
                    description=form.cleaned_data.get('description')
                )
                challenge_template.save()
                challenge.template = challenge_template
            elif step_name == 'choose_club':
                challenge.club_id = form.cleaned_data.get('recipient_club_id')
            elif step_name == 'set_donation_amount':
                challenge.proposed_donation_amount = form.cleaned_data.get('proposed_donation_amount')
            elif step_name == 'update_details':
                challenge.name = form.cleaned_data.get('name')
                challenge.description = form.cleaned_data.get('description')
        challenge.save()
        return HttpResponseRedirect('/challenges/%s' % challenge.id)


class AcceptChallengeWizard(FormWizard):
    TEMPLATES = [
        "spudderspuds/challenges/wizards/accept_challenge/accept_challenge.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_club.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_donation.html",
        "spudderspuds/challenges/wizards/create_challenge/challenge_details.html"
    ]
    FORMS_LIST = [AcceptChallengeForm, ChallengeClubForm, ChallengeDonationForm, ChallengeDetailsForm]
    STEPS = ['accept_challenge', 'choose_club', 'set_donation_amount', 'update_details']

    def __init__(self, *args, **kwargs):
        self.challenge = kwargs.pop('challenge', None)
        super(AcceptChallengeWizard, self).__init__(*args, **kwargs)
        self.extra_context = {
            'challenge': self.challenge,
            'clubs': Club.objects.all()
        }
        self.FILES = {}
        self.initial = {
            2: {'proposed_donation_amount': self.challenge.proposed_donation_amount},
            3: {'name': self.challenge.name, 'description': self.challenge.description}
        }

    def get_template(self, step):
        return [self.TEMPLATES[step]]

    def done(self, request, form_list):
        challenge = Challenge(
            parent=self.challenge,
            template=self.challenge.template,
            creator_entity_id=request.current_role.entity.id,
            creator_entity_type=request.current_role.entity_type
        )
        participation = ChallengeParticipation(
            participating_entity_id=request.current_role.entity.id,
            participating_entity_type=request.current_role.entity_type
        )
        for index, form in enumerate(form_list):
            step_name = self.STEPS[index]
            if step_name == 'accept_challenge':
                participation.donation_amount = form.cleaned_data.get('donation_amount')
                participation.state = ChallengeParticipation.ACCEPTED_STATE
            elif step_name == 'choose_club':
                challenge.recipient_entity_id = form.cleaned_data.get('recipient_club_id')
                challenge.recipient_entity_type = Club.__name__
            elif step_name == 'set_donation_amount':
                challenge.proposed_donation_amount = form.cleaned_data.get('proposed_donation_amount')
            elif step_name == 'update_details':
                challenge.name = form.cleaned_data.get('name')
                challenge.description = form.cleaned_data.get('description')
        challenge.save()
        participation.challenge = challenge
        participation.save()
        return HttpResponseRedirect('/challenges/%s' % challenge.id)
