from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import BookRentalForm, GearRentalForm
from .models import BookRental, GearRental
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
        
        gear_rentals_from_search = list(GearRental.objects.filter(member__in=users))
        for rental in gear_rentals_from_search:
            rental.type = "gear"

        book_rentals_from_search = list(BookRental.objects.filter(member__in=users))
        for rental in book_rentals_from_search:
            rental.type = "book"
        
        rentals_from_search = gear_rentals_from_search + book_rentals_from_search

    current_gear_rentals = list(GearRental.objects.filter(return_date__isnull=True))
    for rental in current_gear_rentals:
        rental.type = "gear"
    overdue_gear_rentals = [rental for rental in current_gear_rentals if rental.due_date < today]
    lost_gear_rentals = [rental for rental in current_gear_rentals if rental.lost]

    current_book_rentals = list(BookRental.objects.filter(return_date__isnull=True))
    for rental in current_book_rentals:
        rental.type = "book"
    overdue_book_rentals = [rental for rental in current_book_rentals if rental.due_date < today]
    lost_book_rentals = [rental for rental in current_book_rentals if rental.lost]

    return render(request, 'gear/gearmaster.html', {
        'rentals': {
            'current': current_gear_rentals + current_book_rentals,
            'overdue': overdue_gear_rentals + overdue_book_rentals,
            'lost': lost_gear_rentals + lost_book_rentals,
            'search': rentals_from_search
        }
    })

@Execs
def create_rental(request, type):
    if type == "gear":
        form_type = GearRentalForm
    elif type == "book":
        form_type = BookRentalForm
    else:
        raise Http404(f"Rental type '${type}' not recognized")
    
    if request.method == "POST":
        form = form_type(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.qm = request.user
            form.save()
            return redirect("rentals")
    else:
        form = form_type()

    return render(request, 'gear/create_rental.html', {
        'form': form,
        'type': type
    })

@Execs
def edit_rental(request, pk, type):
    if type == "gear":
        rental_model = GearRental
        form_type = GearRentalForm
    elif type == "book":
        rental_model = BookRental
        form_type = BookRentalForm
    else:
        raise Http404(f"Rental type '${type}' not recognized")
    
    rental = get_object_or_404(rental_model, pk=pk)

    if request.method == "POST":
        form = form_type(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            return redirect("rentals")
    else:
        form = form_type(instance=rental)

    return render(request, 'gear/edit_rental.html', {
        'form': form,
        'type': type
    })

@Execs
def renew_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)
        print(rental)

        rental.due_date += datetime.timedelta(weeks=1)
        rental.extensions += 1
        rental.save()

    return redirect('rentals')

@Execs
def return_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)

        rental.return_date = timezone.localdate()
        rental.save()

    return redirect('rentals')

@Execs
def lost_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)

        rental.lost = True
        rental.save()

    return redirect('rentals')
