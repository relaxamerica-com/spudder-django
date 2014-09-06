from django.shortcuts import render


def splash(request):
    return render(request, 'spudderclubs/pages/splash.html')