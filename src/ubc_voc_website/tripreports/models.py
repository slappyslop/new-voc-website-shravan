from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class TripReport(Page):
    body = RichTextField(features=["bold", "italic", "link", "image"])

    content_panels = Page.content_panels + [
        FieldPanel('body')
    ]

    parent_page_types = ['tripreports.TripReportIndexPage']

class TripReportIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ['tripreports.TripReport']
