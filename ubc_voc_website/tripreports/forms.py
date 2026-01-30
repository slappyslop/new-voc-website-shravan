from django import forms

from .models import Comment, TripReport, TripReportCategory
from trips.models import Trip

from bs4 import BeautifulSoup
from django_quill.forms import QuillFormField
import json
from wagtail.rich_text import RichText

class TripReportForm(forms.ModelForm):
    class Meta:
        model = TripReport
        fields = ["title", "body", "trip", "categories"]

    def clean_body(self):
        body_data = self.cleaned_data.get("body")
        try:
            body_json = json.loads(body_data)
            body_html = body_json.get("html", "")
            normalized_html = body_html.replace("<br>", "<p></p>")
            soup = BeautifulSoup(normalized_html, "html.parser")
            cleaned_html = soup.decode()
            return RichText(cleaned_html)
        except (ValueError, KeyError, TypeError):
            raise forms.ValidationError("Invalid trip report body format")
        
    def save(self):
        trip_report = super().save(commit=False)
        if "categories" in self.cleaned_data:
            trip_report.categories.clear()
            for category in self.cleaned_data["categories"]:
                trip_report.categories.add(category)
        
        return trip_report

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
        }),
    )
    trip = forms.ModelChoiceField(
        queryset=Trip.objects.all(),
        widget=forms.Select(attrs={"id": "trip-select"}),
        label="Trip (optional)",
        required=False
    )
    body = QuillFormField(label="")  
    categories = forms.ModelMultipleChoiceField(
        queryset=TripReportCategory.objects.all(),
        label="Categories",
        widget=forms.SelectMultiple(attrs={"class": "choices"}),
        required=False
    )

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {
            "body": ""
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment..."})
        }