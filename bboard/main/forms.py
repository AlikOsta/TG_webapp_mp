from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from .models import Bb, AdditionalImage, CustomUser, SuperLocation, SubLocation


class SubLocationForm(forms.ModelForm):
    super_location = forms.ModelChoiceField(
        queryset=SuperLocation.objects.all(),
        empty_label=None,
        label='Страна',
        required=True
    )

    class Meta:
        model = SubLocation
        fields = '__all__'


class BbForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Изображения")

    class Meta:
        model = Bb
        fields = ['rubric', 'title', 'content', 'price', 'currency', 'city']
        widgets = {
            'author': forms.HiddenInput,  # Скрытое поле для автора объявления
        }

    def save(self, commit=True):
        """Сохранение объявления и связанных изображений"""
        bb = super().save(commit=False)
        if commit:
            bb.save()

        # Сохранение изображений, если они были загружены
        images = self.files.getlist('image')
        AdditionalImage.objects.bulk_create(
            [AdditionalImage(bb=bb, image=image) for image in images if image]
        )

        return bb


# Набор форм для добавления/редактирования изображений, связанных с объявлением
AiFormSet = inlineformset_factory(Bb, AdditionalImage, fields='__all__')


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('telegram_id', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """Инициализация формы с настройкой меток полей"""
        super().__init__(*args, **kwargs)
        self.fields['telegram_id'].label = "Telegram ID"
        self.fields['username'].label = "Имя пользователя"


class ChaserUserInfoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'image']
