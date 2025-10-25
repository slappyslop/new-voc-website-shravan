from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string

from .models import Exec, Membership, Profile, PSG, Waiver
from trips.models import Trip, TripSignup, TripSignupTypes
from .forms import ExecForm, MembershipForm, ProfileForm, PSGForm, WaiverForm
from ubc_voc_website.decorators import Admin, Members, Execs

from .utils import *

import base64
import datetime
from weasyprint import HTML
from openpyxl import Workbook

User = get_user_model()

@login_required
def join(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST, user=request.user)
        if form.is_valid():
            membership = form.save()
            if membership.type != Membership.MembershipType.INACTIVE_HONOURARY:
                return redirect(f'waiver/{membership.id}')
            else :
                return redirect('home')
    else:
        form = MembershipForm(user=request.user)
    return render(request, 'membership/join.html', {'form': form})

@login_required
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

@login_required
def waiver(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    if membership.user != request.user:
        return render(request, 'access_denied.html', status=403)
    
    if request.method == "POST":
        form = WaiverForm(request.POST, user=request.user)

        if form.is_valid():
            waiver = form.save(commit=False)
            waiver.membership = membership

            signature_data = form.cleaned_data['signature']
            f, imgstr = signature_data.split(';base64')
            data = ContentFile(base64.b64decode(imgstr))

            waiver.signature.save('signature.png', data, save=False)

            waiver.save()
            return redirect('home')
        
    else:
        form = WaiverForm(user=request.user)

    return render(request, 'membership/waiver.html', {'form': form, 'user_is_minor': is_minor(datetime.datetime.today(), request.user.profile.birthdate)})

@Members
def member_list(request):
    exec_profiles = Profile.objects.filter(user__in=Exec.objects.values('user'))
    execs = []
    for profile in exec_profiles:
        exec = Exec.objects.get(user=profile.user)
        execs.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'position': exec.exec_role,
            'email': profile.user.email,
            'phone': profile.phone
        })

    psg_profiles = Profile.objects.filter(user__in=PSG.objects.values('user'))
    psg_members = []
    for profile in psg_profiles:
        psg_members.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'email': profile.user.email,
            'phone': profile.phone
        })

    member_profiles = Profile.objects.all().exclude(user__in=exec_profiles).exclude(user__in=psg_profiles).filter(user__in=Membership.objects.filter(
            end_date__gte=datetime.date.today(),
            active=True
        ).values('user'))
    members = []
    for profile in member_profiles:
        members.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'email': profile.user.email,
            'phone': profile.phone
        })

    return render(request, 'membership/members.html', {'execs': execs, 'psg_members': psg_members, 'members': members})

@Members
def profile(request, id):
    user = get_object_or_404(User, id=id)
    profile = Profile.objects.get(user=user)

    organized_trips = Trip.objects.filter(organizers=request.user)
    organized_trips_list = {}
    for trip in organized_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in organized_trips_list:
            organized_trips_list[month] = []
        organized_trips_list[month].append(trip)
    organized_trips_list = dict(sorted(organized_trips_list.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y'), reverse=True))

    going_signups = TripSignup.objects.filter(user=request.user, type=TripSignupTypes.GOING)
    attended_trips = [signup.trip for signup in going_signups]
    attended_trips_list = {}
    for trip in attended_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in attended_trips_list:
            attended_trips_list[month] = []
        attended_trips_list[month].append(trip)
    attended_trips_list = dict(sorted(attended_trips_list.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y'), reverse=True))

    gallery = getattr(user, 'gallery', None)

    return render(request, 'membership/profile.html', {
        'user': user, 
        'profile': profile, 
        'trips': {
            'organized': organized_trips_list,
            'attended': attended_trips_list
        },
        'gallery': gallery
    })

@Members
def view_waiver(request, id):
    user = get_object_or_404(User, id=request.user.id)
    membership = get_object_or_404(Membership, id=id)
    waiver = Waiver.objects.get(membership=membership)
    exec = Exec.objects.get(user=user)

    if not waiver:
        return "<p>No waiver found for this membership</p>"
    elif not exec and waiver.user != user:
        # custom access control - Execs can see all waivers but non-Execs can only see their own
        return render(request, 'access_denied.html', status=403)
    else:
        form = WaiverForm(user=user, instance=waiver, readonly=True)
        html_content = render_to_string('membership/waiver_readonly.html', {'form': form, 'waiver': waiver, 'readonly': True})
        base_url = request.build_absolute_uri('/')
        pdf = HTML(string=html_content, base_url=base_url)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="waiver.pdf"'
        response.write(pdf.write_pdf())
        return response

@Execs
def manage_memberships(request):
    # all profiles that have at least 1 membership
    profiles = Profile.objects.filter(user__in=Membership.objects.all().values('user'))

    for profile in profiles:
        profile.memberships = Membership.objects.filter(user=profile.user).order_by('-end_date')

    return render(request, 'membership/manage_memberships.html', {'profiles': profiles})

@Execs
def toggle_membership(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)

    membership.active = not membership.active
    membership.save()

    return redirect('manage_memberships')

@Admin
def manage_roles(request): # for managing who has the exec role
    if request.method == "POST":
        remove_exec = request.POST.get('remove-exec')
        remove_psg = request.POST.get('remove-psg')

        if remove_exec:
            user = get_object_or_404(User, id=remove_exec)
            Exec.objects.filter(user=user).delete()

        elif remove_psg:
            user = get_object_or_404(User, id=remove_psg)
            PSG.objects.filter(user=user).delete()

        elif 'exec-user' in request.POST: # add/modify existing exec
            user = get_object_or_404(User, id=request.POST['exec-user'])
            exec_instance = get_object_or_404(Exec, user=user)
            form = ExecForm(request.POST, instance=exec_instance, prefix='exec')

            if form.is_valid():
                exec = form.save()

            return redirect('manage_roles')
        
        elif 'psg-user' in request.POST: # add/modify existing PSG member
            user = get_object_or_404(User, id=request.POST['psg-user'])
            form  = PSGForm(request.POST, prefix='psg')

            if form.is_valid():
                psg = form.save()

            return redirect('manage_roles')
        
        return redirect('manage_roles')

    else:
        exec_form = ExecForm(prefix="exec")
        psg_form = PSGForm(prefix='psg')

        execs = Exec.objects.all().order_by('exec_role')

        execs_extended_info = []

        for exec in execs:
            profile = Profile.objects.get(user=exec.user)
            execs_extended_info.append({
                'id': exec.user.id,
                'role': exec.exec_role,
                'first_name': profile.first_name,
                'last_name': profile.last_name
            })

        psg = PSG.objects.all()
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
    active_memberships = Membership.objects.filter(
        end_date__gte=datetime.date.today(),
        active=True
    )
    regular_memberships = active_memberships.filter(type=Membership.MembershipType.REGULAR)
    associate_memberships = active_memberships.filter(type=Membership.MembershipType.ASSOCIATE)
    active_honorary_memberships = active_memberships.filter(type=Membership.MembershipType.ACTIVE_HONORARY)
    inactive_honorary_memberships = active_memberships.filter(type=Membership.MembershipType.INACTIVE_HONOURARY)

    inactive_memberships = Membership.objects.filter(
        end_date__gte=datetime.date.today(),
        active=False
    )

    return render(request, 'membership/membership_stats.html', {
            'num_members': active_memberships.count(),
            'num_inactive_memberships': inactive_memberships.count(),
            'num_regular_members': regular_memberships.count(), 
            'num_associate_members': associate_memberships.count(), 
            'num_active_honorary_members': active_honorary_memberships.count(),
            'num_inactive_honorary_members': inactive_honorary_memberships.count()
        })
    
    # TODO add more stats that would be useful/interesting (trip signups, etc.)

@Execs
def download_member_table(request, type):
    if type == "acc":
        memberships = Membership.objects.filter(
            end_date__gte=datetime.date.today(),
            active=True,
            type=Membership.MembershipType.REGULAR
        )
        profiles = Profile.objects.filter(
            user__in=memberships.values_list('user', flat=True), 
            acc=True
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "ACC Membership Candidates"

        fields = ['First Name', 'Last Name', 'Email', 'Phone', 'Birthdate']
        ws.append(fields)

        for profile in profiles:
            row = [
                profile.first_name,
                profile.last_name,
                profile.user.email,
                profile.phone,
                profile.birthdate
            ]
            ws.append(row)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="voc_acc_members.xlsx"'
        wb.save(response)
        return response
    
    elif type == "fmcbc":
        """
            This result is sent to the FMCBC for insurance, so we exclude inactive honorary members
        """
        memberships = Membership.objects.filter(
            end_date__gte=datetime.date.today(),
            active=True
        ).exclude(
            type=Membership.MembershipType.INACTIVE_HONOURARY
        )
        profiles = Profile.objects.filter(user__in=memberships.values_list('user', flat=True))

        wb = Workbook()
        ws = wb.active
        ws.title = "VOC Member List (for FMCBC)"

        fields = ['No.', 'First Name', 'Last Name', 'Email', 'Phone', 'Birthdate']
        ws.append(fields)

        i = 1
        for profile in profiles:
            row = [
                i,
                profile.first_name,
                profile.last_name,
                profile.user.email,
                profile.phone,
                profile.birthdate
            ]
            ws.append(row)
            i += 1

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="voc_members.xlsx"'
        wb.save(response)
        return response

    else:
        return Http404(f"Member list type {type} not found")

