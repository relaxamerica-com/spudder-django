from django.shortcuts import render
from spudmart.venues.models import Venue
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

def view(request, venue_id):
    return render(request, 'venues/view.html')

def create(request):
    if request.method == 'POST' and isinstance(request.user, User):
        venue = Venue(user = request.user)
        venue.save()
        return view(request, venue.id)
    elif request.method == 'POST':
        return HttpResponseRedirect('/accounts/login?next=/venues/create')
    
    return render(request, 'venues/create.html')