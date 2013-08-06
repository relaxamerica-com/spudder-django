'''
Created on 07-07-2013

@author: doop
'''
from django.shortcuts import render

def home(request):
    return render(request, 'home/home.html')