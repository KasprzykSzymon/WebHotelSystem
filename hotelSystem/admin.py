from django.contrib import admin
from .models import SocialApp

@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'client_id')
    filter_horizontal = ('sites',)
