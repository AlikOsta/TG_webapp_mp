from django.contrib import admin
from .models import Bb, Rubric, Currency, Country, City, AdditionalImage, CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserCreationForm
    model = CustomUser
    list_display = ('telegram_id', 'username', 'is_staff', 'is_active',)
    list_filter = ('telegram_id', 'username', 'is_staff', 'is_active',)
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
    search_fields = ('telegram_id', 'username',)
    ordering = ('telegram_id',)

admin.site.register(CustomUser, CustomUserAdmin)


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage
    extra = 1


class BbAdmin(admin.ModelAdmin):
    inlines = [AdditionalImageInline]
    list_display = ('title', 'content', 'price', 'published', 'rubric', "is_active")
    list_display_links = ('title', 'content', )
    search_fields = ('title', 'content', )

admin.site.register(Bb, BbAdmin)
admin.site.register(Rubric)
admin.site.register(Currency)
admin.site.register(Country)
admin.site.register(City)
