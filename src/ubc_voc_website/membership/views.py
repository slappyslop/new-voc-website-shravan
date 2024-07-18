from django.shortcuts import render
from django.db.models import OuterRef, Subquery
from .models import Exec, Membership, Profile
from ubc_voc_website.decorators import Members, Execs

@Members
def member_list(request):
    profiles = Profile.objects.all().filter(user__is_active=True)
    return profiles

@Members
def profile(request, user):
    profile = Profile.objects.get(user=user)
    return render(request, 'profile.html', {'user': user, 'profile': profile})

@Members
def my_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    return render(request, 'profile.html', {'user': user, 'profile': profile})

@Members
def edit_user_profile(request, user):
    profile = Profile.objects.get(user=user)
    return render(request, 'profile.html', {'user': user, 'profile': profile})

@Execs
def manage_roles(request):
    execs = Exec.objects.filter(user=OuterRef('user'))
    profiles = Profile.objects.all().filter(user__in=Subquery(execs.values('user')))
    return profiles

@Execs
def membership_stats(request):
    num_inactive_accounts = Profile.objects.all().filter(user__is_active=False).count()
    num_regular_members = Membership.objects.all().filter(type=Membership.MembershipType.REGULAR).count()
    num_associate_members = Membership.objects.all().filter(type=Membership.MembershipType.ASSOCIATE).count()
    num_honourary_members = Membership.objects.all().filter(type=Membership.MembershipType.HONORARY).count()

    # TODO add more stats that would be useful/interesting (trip signups, etc.)

    return (num_inactive_accounts, num_regular_members, num_associate_members, num_honourary_members)
