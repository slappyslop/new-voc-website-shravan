from django.conf import settings
from django.db import models
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ubc_voc_website.utils import is_member

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

class TripReport(Page):
    body = RichTextField(features=["bold", "italic", "link", "image", "ol", "ul"])
    trip = models.ForeignKey(
        "trips.Trip",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trip_report"
    )

    categories = ParentalManyToManyField("tripreports.TripReportCategory", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('trip'),
        FieldPanel("legacy_pdf")
    ]
    parent_page_types = ['tripreports.TripReportIndexPage']

    old_id = models.IntegerField(blank=True, null=True)
    legacy_pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    def serve(self, request):
        from .forms import CommentForm
        if request.method == "POST":
            if is_member(request.user):
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.trip_report = self
                    comment.user = request.user
                    comment.save()
                    return redirect(self.url)       
        else:
            form = CommentForm()

        context = super().get_context(request)
        context["form"] = form
        context["comments"] = self.comments.all()
        return TemplateResponse(request, self.get_template(request), context)

class Comment(models.Model):
    trip_report = models.ForeignKey(
        TripReport,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class TripReportIndexPage(Page):
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]
    subpage_types = ['tripreports.TripReport']

    def get_context(self, request):
        context = super().get_context(request)
        reports = self.get_children().live().public().specific().order_by("-first_published_at")
        context["reports"] = reports
        context["categories"] = TripReportCategory.objects.all()
        return context
    
@register_snippet
class TripReportCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Trip Report Categories"