from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from ubc_voc_website.utils import *

def Members(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if is_member(request.user):
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def Execs(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if is_exec(request.user):
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def PSG(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if is_PSG(request.user):
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


