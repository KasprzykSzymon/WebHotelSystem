from django.contrib import admin
from .models import SocialApp, Room, Guest, Reservation, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [RoomImageInline]

@admin.register(SocialApp)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'client_id')
    filter_horizontal = ('sites',)

admin.site.register(Guest)
admin.site.register(Reservation)