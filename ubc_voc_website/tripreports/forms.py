from django import forms
from django_quill.forms import QuillFormField

from .models import Comment, TripReport

class TripReportForm(forms.ModelForm):
    class Meta:
        model = TripReport
        fields = ["title", "body", "trip"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "trip": forms.Select(attrs={"class": "form-select"})
        }

    body = QuillFormField()

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