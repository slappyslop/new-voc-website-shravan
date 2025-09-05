from django.shortcuts import render, redirect
from wagtail.models import Page
from ubc_voc_website.decorators import Members

from .models import TripReport, TripReportIndexPage
from .forms import TripReportForm

@Members
def create_trip_report(request):
    parent = TripReportIndexPage.objects.first()

    if request.method == "POST":
        form = TripReportForm(request.POST)
        if form.is_valid():
            trip_report = form.save(commit=False)
            trip_report.owner = request.user

            parent.add_child(instance=trip_report)

            revision = trip_report.save_revision(user=request.user)
            if "submit" in request.POST: # Submit for approval
                revision.submit_for_moderation()

            return redirect(parent.url)
    else:
        form = TripReportForm()

    return render(request, "tripreports/create_trip_report.html", {"form": form})

@Members
def my_tripreports(request):
    tripreports = TripReport.objects.filter(owner=request.user)

    return render(request, "tripreports/my_tripreports.html", {
        "tripreports": tripreports
    })
        