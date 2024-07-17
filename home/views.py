from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .dash_apps.finished_apps.dashProyecto import dashboard
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View


def loginfull(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'home/welcome.html')


class Dashboard_view(LoginRequiredMixin,View):
    def get(self,request):
        #profile = Profile.objects.get(user_id = self.request.user.id)
        #print(profile.company.avatar_profile)
        context = {
            'dashboard': dashboard( self.request.user.id ),
        }
        return render(request, 'home/dashboard.html', context)