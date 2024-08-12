from django.forms import ModelForm
from django import forms
from .models import Bb, AdditionalImage


class BbForm(forms.ModelForm):
    images = forms.ImageField(
        widget=forms.FileInput(attrs={'multiple': False}),
        required=False
    )

    class Meta:
        model = Bb
        fields = ['rubric', 'title', 'content', 'images', 'price', 'currency', 'city', ]

    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 5:
            raise forms.ValidationError("Нельзя загрузить более 5 изображений.")
        return images

    def save(self, commit=True):
        bb = super().save(commit=False)
        if commit:
            bb.save()
        images = self.cleaned_data['images']
        for image in images:
            AdditionalImage.objects.create(bb=bb, image=image)
        return bb
