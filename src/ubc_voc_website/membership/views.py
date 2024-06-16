from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    return render(request, 'profile.html', {'user': user, 'profile': profile})
