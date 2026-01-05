from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Exec, Membership, Profile, PSG, Waiver
from trips.models import Trip, TripSignup, TripSignupTypes
from .forms import MembershipForm, ProfileForm, WaiverForm
from ubc_voc_website.decorators import Members, Execs

from .utils import *
from ubc_voc_website.utils import is_member

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
                return redirect('waiver', membership.id)
            else :
                return redirect('home')
    else:
        form = MembershipForm(user=request.user)
        start_date = timezone.localdate()
        end_date = get_end_date(timezone.localdate())

    return render(request, 'membership/join.html', {
        'form': form,
        'start_date': start_date,
        'end_date': end_date    
    })

@login_required
def edit_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', profile.user.id)
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

    return render(request, 'membership/waiver.html', {'form': form, 'user_is_minor': is_minor(timezone.localdate(), request.user.profile.birthdate)})

@Members
def member_list(request):
    exec_queryset = Exec.objects.select_related('user', 'user__profile').order_by('priority', 'user__profile__first_name')
    execs = []
    for exec in exec_queryset:
        profile = exec.user.profile
        execs.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'position': exec.exec_role,
            'email': profile.user.email,
            'phone': profile.phone
        })

    psg_queryset = PSG.objects.select_related('user', 'user__profile').order_by('user__profile__first_name')
    psg_members = []
    for psg in psg_queryset:
        profile = psg.user.profile
        psg_members.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'email': profile.user.email,
            'phone': profile.phone
        })

    exec_user_ids = Exec.objects.values_list('user_id', flat=True)
    psg_user_ids = PSG.objects.values_list('user_id', flat=True)
    member_profiles = Profile.objects.all().exclude(user_id__in=exec_user_ids).exclude(user_id__in=psg_user_ids).filter(user__in=Membership.objects.filter(
            end_date__gte=timezone.localdate(),
            active=True
        ).values('user')).order_by('first_name', 'last_name')
    members = []
    for profile in member_profiles:
        members.append({
            'id': profile.user.id,
            'name': f'{profile.first_name} {profile.last_name}',
            'email': profile.user.email,
            'phone': profile.phone
        })

    return render(request, 'membership/members.html', {'execs': execs, 'psg_members': psg_members, 'members': members})

@login_required
def profile(request, id):
    user = get_object_or_404(User, id=id)
    if not is_member(request.user) and user != request.user: # Non-members can only view their own profile
        return render(request, 'access_denied.html', status=403)
    else:
        profile = Profile.objects.get(user=user)

        organized_trips = Trip.objects.filter(organizers=user)
        organized_trips_list = {}
        for trip in organized_trips:
            month = trip.start_time.strftime('%B %Y')
            if month not in organized_trips_list:
                organized_trips_list[month] = []
            organized_trips_list[month].append(trip)
        organized_trips_list = dict(sorted(organized_trips_list.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y'), reverse=True))

        going_signups = TripSignup.objects.filter(user=user, type=TripSignupTypes.GOING)
        attended_trips = [signup.trip for signup in going_signups]
        attended_trips_list = {}
        for trip in attended_trips:
            month = trip.start_time.strftime('%B %Y')
            if month not in attended_trips_list:
                attended_trips_list[month] = []
            attended_trips_list[month].append(trip)
        attended_trips_list = dict(sorted(attended_trips_list.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y'), reverse=True))

        return render(request, 'membership/profile.html', {
            'user': user, 
            'profile': profile, 
            'trips': {
                'organized': organized_trips_list,
                'attended': attended_trips_list
            }
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
    latest_membership_subquery = Membership.objects.filter(user=OuterRef('user_id')).order_by('-end_date').values('id')[:1]
    profile_queryset = Profile.objects.filter(user__membership__isnull=False).distinct().order_by('first_name', 'last_name')
    profile_queryset = profile_queryset.annotate(latest_membership_id=Subquery(latest_membership_subquery)).select_related('user')
    profile_list = list(profile_queryset)

    latest_memberships = Membership.objects.filter(
        id__in=[p.latest_membership_id for p in profile_list if p.latest_membership_id]
    )
    membership_map = {m.user_id: m for m in latest_memberships}

    for profile in profile_list:
        profile.latest_membership = membership_map.get(profile.user.id)

    return render(request, 'membership/manage_memberships.html', {'profiles': profile_list})

@Execs
def get_memberships_for_user(request, id):
    user = get_object_or_404(User, id=id)
    memberships = user.membership_set.order_by('-end_date')
    return render(request, 'membership/partial/memberships_table.html', {'memberships': memberships})

@Execs
def toggle_membership(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)

    membership.active = not membership.active
    membership.save()

    return redirect('manage_memberships')

@Execs
def membership_stats(request):
    active_memberships = Membership.objects.filter(
        end_date__gte=timezone.localdate(),
        active=True
    )
    regular_memberships = active_memberships.filter(type=Membership.MembershipType.REGULAR)
    associate_memberships = active_memberships.filter(type=Membership.MembershipType.ASSOCIATE)
    active_honorary_memberships = active_memberships.filter(type=Membership.MembershipType.ACTIVE_HONORARY)
    inactive_honorary_memberships = active_memberships.filter(type=Membership.MembershipType.INACTIVE_HONOURARY)

    inactive_memberships = Membership.objects.filter(
        end_date__gte=timezone.localdate(),
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
            end_date__gte=timezone.localdate(),
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
            end_date__gte=timezone.localdate(),
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

