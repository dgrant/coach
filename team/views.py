from django.http import HttpResponse
from django.shortcuts import render

from django.shortcuts import render

# Create your views here.
def home_page(request):
    return HttpResponse('<html><title>Team Manager</title></html>')
