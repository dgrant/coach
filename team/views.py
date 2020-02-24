from django.shortcuts import render, redirect

from team.models import Team


def home_page(request):
    if request.method == 'POST':
        Team.objects.create(name=request.POST.get('team_name'))
        return redirect("/")

    teams = Team.objects.all()
    return render(request, 'home.html', {"teams": teams})
