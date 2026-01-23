from django.shortcuts import get_object_or_404, render, redirect

from .forms import TripReportForm
from .models import TripReport, TripReportIndexPage
from ubc_voc_website.decorators import Members

@Members
def trip_report_create(request):
    parent = TripReportIndexPage.objects.first()
    if request.method == "POST":
        form = TripReportForm(request.POST)
        if form.is_valid():
            trip_report = form.save()
            trip_report.owner = request.user
            trip_report.live = False

            parent.add_child(instance=trip_report)
            revision = trip_report.save_revision(user=request.user)

            if "submit" in request.POST: # Submit for approval
                workflow = trip_report.get_workflow()
                workflow.start(trip_report, request.user)

            return redirect("my_trip_reports")
    else:
        form = TripReportForm()

    return render(request, "tripreports/trip_report_form.html", {
        "form": form,
        "action": "create"
    })

@Members
def trip_report_edit(request, id):
    trip_report = get_object_or_404(TripReport, id=id)

    if trip_report.live:
        return redirect(trip_report.url)

    if trip_report.owner != request.user:
        return render(request, 'access_denied.html', status=403)
    
    if request.method == "POST":
        form = TripReportForm(request.POST, instance=trip_report)
        if form.is_valid():
            trip_report = form.save()
            revision = trip_report.save_revision(user=request.user)

            if "submit" in request.POST: # Submit for approval
                workflow = trip_report.get_workflow()
                workflow.start(trip_report, request.user)
                
            return redirect("my_trip_reports")
    else:
        form = TripReportForm(instance=trip_report)

    return render(request, "tripreports/trip_report_form.html", {
        "form": form,
        "action": "edit"
    })

@Members
def my_trip_reports(request):
    trip_reports = TripReport.objects.filter(owner=request.user).order_by("live", "-first_published_at")
    return render(request, "tripreports/my_trip_reports.html", {
        "trip_reports": trip_reports
    })