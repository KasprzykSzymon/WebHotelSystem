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

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'check_in_date', 'check_out_date', 'total_price')