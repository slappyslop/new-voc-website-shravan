from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Exec, Membership, Profile, PSG
from ubc_voc_website.decorators import Members, Execs
from .forms import ExecForm, MembershipForm, ProfileForm, PSGForm, WaiverForm
from django.http import HttpResponseForbidden
from django.core.files.base import ContentFile

import base64

User = get_user_model()

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
    user = get_object_or_404(User, id=id)
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
def manage_roles(request): # for managing who has the exec role
    exec_group, created = Group.objects.get_or_create(name='Exec')
    psg_group, created = Group.objects.get_or_create(name='PSG')

    if request.method == "POST":
        if 'exec-user' in request.POST:
            user = get_object_or_404(User, id=request.POST['exec-user'])
            exec_instance = get_object_or_404(Exec, user=user)
            form = ExecForm(request.POST, instance=exec_instance, prefix='exec')

            if form.is_valid():
                exec = form.save()
                exec_group.user_set.add(exec.user)

            return redirect('manage_roles')
        
        elif 'psg-user' in request.POST:
            user = get_object_or_404(User, id=request.POST['psg-user'])
            form  = PSGForm(request.POST, prefix='psg')

            if form.is_valid():
                psg = form.save()
                psg_group.user_set.add(user)

            return redirect('manage_roles')

    else:
        exec_form = ExecForm(prefix="exec")
        psg_form = PSGForm(prefix='psg')

        # Ignore anyone who has somehow ended up with an entry in the exec table without the group role, although this should (hopefully) never happen
        execs = Exec.objects.filter(user__groups__id=exec_group.id).order_by('exec_role')

        execs_extended_info = []

        for exec in execs:
            profile = Profile.objects.get(user=exec.user)
            execs_extended_info.append({
                'id': exec.user.id,
                'role': exec.exec_role,
                'first_name': profile.first_name,
                'last_name': profile.last_name
            })

        psg = PSG.objects.filter(user__groups__id=psg_group.id)
        psg_extended_info = []

        for member in psg:
            profile = Profile.objects.get(user=member.user)
            psg_extended_info.append({
                'id': member.user.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name
            })

        return render(request, 'membership/manage_roles.html', {
            'execs': execs_extended_info, 
            'psg': psg_extended_info,
            'exec_form': exec_form,
            'psg_form': psg_form
        })

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
