from django.http import HttpResponse

"""

Serves as the API Service's landing page

"""


def home(request):
    return HttpResponse("Landing Page Content")
