from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from spudderdomain.forms import NewChallengeTemplateForm, ChallengeClubForm, ChallengeDonationForm,\
    ChallengeDetailsForm, ChooseChallengeTemplateForm
from spudderdomain.models import ChallengeTemplate, Club, Challenge


def get_challenges(request):
    challenges = Challenge.objects.select_related('template').order_by('-created')
    template_data = {'challenges': challenges}
    return render(request, 'spudderspuds/challenges/pages/challenges.html', template_data)


def new_challenge_wizard_view(request):
    if request.user.is_authenticated():
        wizard = NewChallengeWizard()
        return wizard(request)
    else:
        request.session['redirect_after_auth'] = '/challenges/create'
        return HttpResponseRedirect('/spuds/register')


class NewChallengeWizard(FormWizard):
    TEMPLATES = [
        "spudderspuds/challenges/wizard/choose_challenge_template.html",
        "spudderspuds/challenges/wizard/new_challenge_template.html",
        "spudderspuds/challenges/wizard/challenge_club.html",
        "spudderspuds/challenges/wizard/challenge_donation.html",
        "spudderspuds/challenges/wizard/challenge_details.html"
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
            creator_entity_type=request.current_role.entity_type
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
        # TODO: redirect to challenge page
        return HttpResponseRedirect('/challenges')
