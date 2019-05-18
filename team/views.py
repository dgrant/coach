from django.http import HttpResponse
from django.shortcuts import render


def home_page(request):
    if request.method == 'POST':
        return HttpResponse(request.POST['team_name'])
    return render(request, 'home.html')
