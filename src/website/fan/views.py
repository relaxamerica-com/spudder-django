'''
Created on 17-08-2013

@author: doop
'''
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def spuds(request):
    return render(request, 'fan/spuds.html')

def fans(request):
    return render(request, 'fan/fans.html')

def public_view(request, user_id):
    user = get_object_or_404(User, pk = user_id)
    return render(request, 'fan/public_view.html', { 'user' : user })