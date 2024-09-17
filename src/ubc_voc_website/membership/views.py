from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import OuterRef, Subquery
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Exec, Membership, Profile
from ubc_voc_website.decorators import Members, Execs
from .forms import MembershipForm, ProfileForm, WaiverForm
from django.http import HttpResponseForbidden
from django.core.files.base import ContentFile

import base64

@login_required
def apply(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST, user=request.user)
        if form.is_valid():
            membership = form.save()
            return redirect(f'waiver/{membership.id}')
    else:
        form = MembershipForm(user=request.user)
    return render(request, 'membership/apply.html', {'form': form})

@login_required
def waiver(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    if membership.user != request.user:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        form = WaiverForm(request.POST, user=request.user)
        if form.is_valid():
            waiver = form.save(commit=False)
            waiver.membership = membership
            signature_data = request.POST['signature']

            f, imgstr = signature_data.split(';base64')
            data = ContentFile(base64.base64decode(imgstr))

            waiver.signature.save('signature.png', data, save=False)

            waiver = form.save()
            return redirect('home')
        
    else:
        form = WaiverForm(user=request.user)

    return render(request, 'membership/waiver.html', {'form': form})

@Members
def member_list(request):
    members = Profile.objects.all().filter(user__is_active=True)
    return render(request, 'membership/members.html', {'members': list(members)})

@Members
def profile(request, id):
    user = get_object_or_404(get_user_model(), id=id)
    profile = Profile.objects.get(user=user)
    return render(request, 'membership/profile.html', {'user': user, 'profile': profile})

@Members
def edit_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(f'profile/{user.id}')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'membership/edit_profile.html', {'form': form})

@Execs
def manage_roles(request): # not sure what i had in mind for this one but i'll sort it out later
    execs = Exec.objects.filter(user=OuterRef('user'))
    users = Profile.objects.all().filter(user__in=Subquery(execs.values('user')))
    return render(request, 'membership/manage_roles.html', {'execs': execs, 'users': users})

@Execs
def membership_stats(request):
    num_inactive_accounts = Profile.objects.all().filter(user__is_active=False).count()
    num_regular_members = Membership.objects.all().filter(type=Membership.MembershipType.REGULAR).count()
    num_associate_members = Membership.objects.all().filter(type=Membership.MembershipType.ASSOCIATE).count()
    num_honourary_members = Membership.objects.all().filter(type=Membership.MembershipType.HONORARY).count()
    return render(request, 'membership/membership_stats.html', {
         'num_inactive_accounts': num_inactive_accounts, 
         'num_regular_members': num_regular_members, 
         'num_associate_members': num_associate_members, 
         'num_honourary_members': num_honourary_members
        })
    
    # TODO add more stats that would be useful/interesting (trip signups, etc.)
