from django.contrib import admin
from .models import SocialApp, Room, Guest, Reservation

@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'client_id')
    filter_horizontal = ('sites',)

admin.site.register(Room)
admin.site.register(Guest)
admin.site.register(Reservation)