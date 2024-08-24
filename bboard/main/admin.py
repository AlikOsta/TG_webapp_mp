from django.contrib import admin
from .models import Bb, Rubric, Currency, SuperLocation, SubLocation, AdditionalImage, CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, SubLocationForm


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



class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage
    extra = 1


class SubLocationInline(admin.TabularInline):
    model = SubLocation


class SuperLocationAdmin(admin.ModelAdmin):
    exclude = ("super_location",)
    inlines = (SubLocationInline,)


class SubLocationAdmin(admin.ModelAdmin):
    form = SubLocationForm


class BbAdmin(admin.ModelAdmin):
    inlines = [AdditionalImageInline]
    list_display = ('title', 'content', 'price', 'published', 'rubric', "is_active", 'author')
    list_display_links = ('title', 'content', )
    search_fields = ('title', 'content', )

    list_filter = ('author', 'rubric', 'city')


admin.site.register(Bb, BbAdmin)
admin.site.register(Rubric)
admin.site.register(Currency)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SuperLocation, SuperLocationAdmin)
admin.site.register(SubLocation, SubLocationAdmin)
