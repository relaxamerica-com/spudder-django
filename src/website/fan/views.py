'''
Created on 17-08-2013

@author: doop
'''
from django.shortcuts import render

def spuds(request):
    return render(request, 'fan/spuds.html')

def fans(request):
    return render(request, 'fan/fans.html')