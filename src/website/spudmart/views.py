from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render

@csrf_protect
def home(request):
    return render(request, 'spudmart/home.html')

@csrf_protect
def offer(request):
    return render(request, 'spudmart/offer.html')