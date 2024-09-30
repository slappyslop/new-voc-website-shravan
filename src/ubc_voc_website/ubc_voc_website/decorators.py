from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def Members(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if request.user.groups.filter(name='Members').exists():
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def Execs(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if request.user.groups.filter(name='Exec').exists():
            return view_function(request, *args, **kwargs)
        else:
            return render(request, 'access_denied.html', status=403)
    return _view

def PSG(view_function):
    @login_required
    def _view(request, *args, **kwargs):
        if request.user.groups.filter(name='PSG').exists():
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


