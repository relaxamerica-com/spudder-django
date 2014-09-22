from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from spudderaccounts.utils import change_current_role
from spudderdomain.controllers import RoleController
from spudderdomain.models import Club, TempClub, FanPage, Challenge
from spudderspuds.challenges.forms import CreateTempClubForm, ChallengeDonationAmountForm, ChallengesRegisterForm, ChallengesSigninForm
from spudderspuds.challenges.models import TempClubOtherInformation
from spudderspuds.utils import create_and_activate_fan_role
from spudmart.CERN.models import STATES

_CHALLENGE_TEMPLATES = {
    'icebucket': {
        'id': 1,
        'name': 'The Ice Bucket Challenge',
        'description': 'You know it and you love it, what a great way to raise money!',
        'slug': 'icebucket'
    }
}


def _get_challenge_template(template_id):
    return _CHALLENGE_TEMPLATES['icebucket']


def _get_clubs_by_state(state):
    clubs = [c for c in Club.objects.all()]  # TODO this needs to take into account state
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
        return redirect('/challenges/create/register?next=/challenges/create')
    template_data = {'templates': _CHALLENGE_TEMPLATES.values()}
    return render(request, 'spudderspuds/challenges/pages/create_challenge_choose_template.html', template_data)


def create_challenge_choose_club_choose_state(request, template_id):
    template_data = {
        'template': _get_challenge_template(template_id),
        'states': sorted([{'id': k, 'name': v} for k, v in STATES.items()], key=lambda x: x['id'])}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_choose_club_choose_state.html',
        template_data)


def create_challenge_choose_club(request, template_id, state):
    template_data = {
        'state': STATES[state],
        'template': _get_challenge_template(template_id),
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
            return redirect('/challenges/create/%s/%s/t/%s' % (template_id, state, temp_club.id))
    template_data = {
        'form': form,
        'state': STATES[state],
        'template': _get_challenge_template(template_id)}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_choose_club_create_club.html',
        template_data)


def create_challenge_set_donation(request, template_id, state, club_id, club_class):
    club = get_object_or_404(club_class, id=club_id)
    form = ChallengeDonationAmountForm()
    if request.method == 'POST':
        form = ChallengeDonationAmountForm(request.POST)
        if form.is_valid():
            donation_accept = form.cleaned_data.get('donation_with_challenge')
            donation_reject = form.cleaned_data.get('donation_without_challenge')
            challenge = Challenge()
    template_data = {
        'club': club,
        'club_class': club_class.__name__,
        'form': form,
        'state': state,
        'template': _get_challenge_template(template_id)}
    return render(
        request,
        'spudderspuds/challenges/pages/create_challenge_choose_donation.html',
        template_data)