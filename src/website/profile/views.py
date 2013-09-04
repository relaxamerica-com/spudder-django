'''
Created on 17-08-2013

@author: doop
'''
from django.shortcuts import render
from website.profile.models import ProfileType
from django.http import HttpResponseRedirect

def index(request):
    profile = request.user.get_profile()
    if profile.type == ProfileType.FAN:
        return HttpResponseRedirect('/fan/spuds')
    return render(request, 'profile/index.html')