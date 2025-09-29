from django.conf import settings
from django.db import models
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class TripReport(Page):
    body = RichTextField(features=["bold", "italic", "link", "image"])
    trip = models.ForeignKey(
        "trips.Trip",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="trip_report"
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('trip')
    ]

    parent_page_types = ['tripreports.TripReportIndexPage']

    def serve(self, request):
        from .forms import CommentForm

        if request.method == "POST":
            if request.user.is_authenticated:
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
