from django.forms import ModelForm
from django import forms

from .models import Bb


class BbForm(ModelForm):
    class Meta:
        model = Bb
        fields = ('rubric', 'title', 'content', 'price', "currency", "city")

