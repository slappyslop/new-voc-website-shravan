from django.shortcuts import get_object_or_404, render, redirect
from ubc_voc_website.decorators import Admin, Members, Execs
from ubc_voc_website.utils import is_member

from .models import TripReport, TripReportPrivacyStatus, TripReportStatus
from .forms import TripReportForm

def trip_reports(request):
    if is_member(request.user):
        trip_reports = TripReport.objects.filter(status=TripReportStatus.PUBLISHED)
    else:
        trip_reports = TripReport.objects.filter(status=TripReportStatus.PUBLISHED, privacy=TripReportPrivacyStatus.PUBLIC)

    return render(request, 'trip_reports/trip_reports.html', {'trip_reports': trip_reports})

@Members
def my_trip_reports(request):
    trip_reports = TripReport.objetcs.filter(author=request.user)

    return render(request, 'trip_reports/my_trip_reports.html', {'trip_reports': trip_reports})

@Members
def create_trip_report(request):
    if request.method == "POST":
        form = TripReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trip_reports')
    else:
        form = TripReportForm()
    return render(request, 'trip_reports/trip_report_form.html', {'form': form})

@Members
def edit_trip_report(request, id):
    trip_report = get_object_or_404(TripReport, id=id)

    if not trip_report.authors.filter(pk=request.user.pk).exists():
        return render(request, 'access_denied.html', status=403)
    else:
        if request.method == "POST":
            form = TripReportForm(request.POST, instance=trip_report)
            if form.is_valid():
                form.save()
                return redirect('trip_reports')
            else:
                print(form.errors)
        else:
            form = TripReportForm(instance=trip_report)
        return render(request, 'trip_reports.trip_report_form.html', {'form': form})

@Members
def delete_trip_report(request, id):
    trip_report = get_object_or_404(TripReport, id=id)
    if not trip_report.authors.filter(pk=request.user.pk).exists():
        return render(request, 'access_dennied.html', status=403)
    else:
        trip_report.delete()
        return redirect('trip_reports')

def view_trip_report(request, id):
    trip_report = get_object_or_404(TripReport, id=id)
    return render(request, 'trip_reports/trip_report.hmtl', {'trip_report': trip_report})


