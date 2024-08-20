from django.contrib import admin
from .models import Bb, Rubric, Currency, Country, City, AdditionalImage, CustomUser


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
admin.site.register(CustomUser)
