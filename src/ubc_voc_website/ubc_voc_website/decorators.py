from django.contrib.auth.decorators import login_required
from django.shortcuts import render

import datetime
from membership.models import Exec, Membership, PSG

def Members(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        active_memberships = Membership.objects.filter(
            user=request.user,
            end_date__gte=datetime.datetime.today(),
            active=True
        )

        if active_memberships.count() == 1:
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def Execs(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        exec_positions = Exec.objects.filter(user=request.user)
        if exec_positions.count() >= 1:
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def PSG(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        psg_positions = PSG.objects.filter(user=request.user)
        if psg_positions.count() >= 1:
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def Admin(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view


