from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import BookRentalForm, GearRentalForm
from .models import BookRental, GearRental
from ubc_voc_website.decorators import Execs

import datetime

User = get_user_model()

@Execs
def rentals(request):
    today = timezone.localdate()

    all_gear_rentals = list(GearRental.objects.all())
    for rental in all_gear_rentals:
        rental.type = "gear"
    current_gear_rentals = [rental for rental in all_gear_rentals if not rental.return_date and not rental.lost]
    overdue_gear_rentals = [rental for rental in current_gear_rentals if rental.due_date < today]
    long_gear_rentals = [rental for rental in overdue_gear_rentals if rental.due_date < (today - datetime.timedelta(weeks=3))]

    all_book_rentals = list(BookRental.objects.all())
    for rental in all_book_rentals:
        rental.type = "book"
    current_book_rentals = [rental for rental in all_book_rentals if not rental.return_date and not rental.lost]
    overdue_book_rentals = [rental for rental in current_book_rentals if rental.due_date < today]
    long_book_rentals = [rental for rental in overdue_book_rentals if rental.due_date < (today - datetime.timedelta(weeks=3))]

    return render(request, 'gear/gearmaster.html', {
        'rentals': {
            'current': current_gear_rentals + current_book_rentals,
            'overdue': overdue_gear_rentals + overdue_book_rentals,
            'long': long_gear_rentals + long_book_rentals,
            'all': all_gear_rentals + all_book_rentals
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
