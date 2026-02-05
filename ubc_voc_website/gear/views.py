from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import RentalForm
from .models import Rental
from ubc_voc_website.decorators import Execs

import datetime

User = get_user_model()

today = timezone.localdate()

@Execs
def rentals(request):
    q = request.GET.get("q")
    rentals_from_search = []

    if q:
        name_filter = Q()
        for term in q.strip().split():
            name_filter &= (
                Q(profile__first_name__icontains=term) |
                Q(profile__last_name__icontains=term)
            )

        users = User.objects.select_related("profile").filter(
                name_filter |
                Q(email__icontains=q)
            )
        
        rentals_from_search = list(Rental.objects.filter(member__in=users))

    current_rentals = Rental.objects.filter(return_date__isnull=True)
    overdue_rentals = [rental for rental in current_rentals if rental.due_date < today]
    lost_rentals = Rental.objects.filter(lost=True)

    return render(request, 'gear/gearmaster.html', {
        'rentals': {
            'current': current_rentals,
            'overdue': overdue_rentals,
            'lost': lost_rentals,
            'search': rentals_from_search
        }
    })

@Execs
def create_rental(request):
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.qm = request.user
            form.save()
            return redirect("rentals")
    else:
        form = RentalForm()

    return render(request, 'gear/create_rental.html', {
        'form': form,
        'type': type
    })

@Execs
def edit_rental(request, id):
    rental = get_object_or_404(Rental, id=id)

    if request.method == "POST":
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            return redirect("rentals")
    else:
        form = RentalForm(instance=rental)

    return render(request, 'gear/edit_rental.html', {
        'form': form,
        'type': type
    })

@Execs
def renew_rental(request, id):
    if request.method == "POST":
        rental = get_object_or_404(Rental, id=id)
        rental.due_date += datetime.timedelta(weeks=1)
        rental.extensions += 1
        rental.save()

    return redirect('rentals')

@Execs
def return_rental(request, id):
    if request.method == "POST":
        rental = get_object_or_404(Rental, id=id)
        rental.return_date = timezone.localdate()
        rental.save()

    return redirect('rentals')

@Execs
def lost_rental(request, id):
    if request.method == "POST":
        rental = get_object_or_404(Rental, id=id)
        rental.lost = True
        rental.save()

    return redirect('rentals')
