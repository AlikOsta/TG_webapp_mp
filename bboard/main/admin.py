from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bb, Rubric, Currency, SuperLocation, SubLocation, AdditionalImage, CustomUser
from .forms import CustomUserCreationForm, SubLocationForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserCreationForm
    model = CustomUser
    list_display = ('telegram_id', 'username', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('telegram_id', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('telegram_id', 'username')
    ordering = ('telegram_id',)


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage
    extra = 1
    verbose_name = "Дополнительное изображение"
    verbose_name_plural = "Дополнительные изображения"


class SubLocationInline(admin.TabularInline):
    model = SubLocation
    extra = 1
    verbose_name = "Подлокация"
    verbose_name_plural = "Подлокации"


@admin.register(SuperLocation)
class SuperLocationAdmin(admin.ModelAdmin):
    exclude = ("super_location",)
    inlines = [SubLocationInline]
    list_display = ('name', 'order')
    search_fields = ('name',)
    ordering = ('order', 'name')


@admin.register(SubLocation)
class SubLocationAdmin(admin.ModelAdmin):
    form = SubLocationForm
    list_display = ('name', 'super_location', 'order')
    search_fields = ('name', 'super_location__name')
    ordering = ('super_location__order', 'order', 'name')


@admin.register(Bb)
class BbAdmin(admin.ModelAdmin):
    inlines = [AdditionalImageInline]
    list_display = ('title', 'content', 'price', 'published', 'rubric', "is_active", 'author')
    list_display_links = ('title', 'content')
    search_fields = ('title', 'content')
    list_filter = ('author', 'rubric', 'city')
    ordering = ('-published',)

# Регистрация остальных моделей без кастомизации
admin.site.register(Rubric)
admin.site.register(Currency)
