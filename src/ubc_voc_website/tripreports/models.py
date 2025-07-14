from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class TripReports(models.Model):
    body = RichTextField(features=["bold", "italic", "link", "image"])

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]