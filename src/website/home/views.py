'''
Created on 07-07-2013

@author: doop
'''
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.shortcuts import render

@csrf_protect
def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile')
    registration_activation_complete = True if 'registration_activation_complete' in request.GET else False
    return render(request, 'home/home.html', { 'registration_activation_complete' : registration_activation_complete })
