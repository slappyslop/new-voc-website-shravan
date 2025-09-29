from django.urls import path, include

from . import views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images import urls as wagtailimages_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("images", include(wagtailimages_urls)),
    path("create/", views.trip_report_create, name="trip_report_create"),
    path("edit/<int:id>", views.trip_report_edit, name="trip_report_edit"),
    path("my-trip-reports/", views.my_trip_reports, name="my_trip_reports"),
    path("", include(wagtail_urls))
]