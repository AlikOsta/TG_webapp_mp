from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .compress import compress_image

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
    images = forms.ImageField(
        required=False,
        label="Изображения",
        widget=forms.FileInput(attrs={'multiple': False})  # Изменили ClearableFileInput на FileInput
    )

    class Meta:
        model = Bb
        fields = ['rubric', 'title', 'content', 'price', 'currency', 'city']

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        # Сохранение дополнительных изображений
        images = self.files.getlist('images')
        for image in images:
            if image:
                compressed_image = compress_image(image)
                AdditionalImage.objects.create(bb=instance, image=compressed_image)

        return instance


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


# форма поиска
class SearchForm(forms.Form):
    keywords = forms.CharField(required=False, max_length=20, label='')