from django.forms import ModelForm
from django import forms
from .models import Bb, AdditionalImage


class BbForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Изображения")

    class Meta:
        model = Bb
        fields = ['rubric', 'title', 'content', 'price', 'currency', 'city']

    def save(self, commit=True):
        bb = super().save(commit=False)
        if commit:
            bb.save()
        images = self.files.getlist('image')
        for image in images:
            if image:
                AdditionalImage.objects.create(bb=bb, image=image)
        return bb


