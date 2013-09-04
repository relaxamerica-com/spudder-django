'''
Created on 15-08-2013

@author: doop
'''
from django.shortcuts import render

def league_or_tournament(request):
    return render(request, 'league_or_tournament/league_or_tournament.html')