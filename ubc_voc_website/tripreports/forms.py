from django import forms

from .models import Comment, TripReport
from trips.models import Trip

from django_quill.forms import QuillFormField, QuillWidget
import json

class TripReportForm(forms.ModelForm):
    class Meta:
        model = TripReport
        fields = ["title", "body", "trip"]

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
    body = QuillFormField(
        widget=QuillWidget(attrs={
            "style": "min-height: 400px;"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        body_str = cleaned_data.get('body')
        if body_str:
            body_json = json.loads(body_str)
            html_content = body_json.get("html", "")
            cleaned_data["body"] = html_content.strip() if html_content else ""
        else:
            cleaned_data["body"] = ""
        
        return cleaned_data

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