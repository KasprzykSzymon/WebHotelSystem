from django.db import models
from django.contrib.sites.models import Site
from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta

class Room(models.Model):
     ROOM_TYPES = [
         ('single', 'Single'),
         ('double', 'Double'),
         ('suite', 'Suite'),
     ]

     number = models.CharField(max_length=10, unique=True)
     room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
     price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
     is_available = models.BooleanField(default=True)
     last_minute_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0) #Last minute discount in percent
     # image = models.ImageField(upload_to='images/room_images/')
     def discounted_price(self):

         "Oblicza cene po znizce"
         return self.price_per_night * (1 - self.last_minute_discount / 100)

     def __str__(self):
        return f"Room {self.number} ({self.get_room_type_display()})"

     class Meta:
         verbose_name = "Pokój"
         verbose_name_plural = "Pokoje"

class Guest(models.Model):
     first_name = models.CharField(max_length=50)
     last_name = models.CharField(max_length=50)
     email = models.EmailField(unique=True)
     phone_number = models.CharField(max_length=15)

     def __str__(self):
         return f"{self.first_name} {self.last_name}"

     class Meta:
         verbose_name = "Klient"
         verbose_name_plural = "Klienci"

class Reservation(models.Model):
     room = models.ForeignKey(Room, on_delete=models.CASCADE)
     guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
     check_in_date = models.DateField()
     check_out_date = models.DateField()
     total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

     def save(self, *args, **kwargs):
         nights = (self.check_out_date - self.check_in_date).days
         self.total_price = nights * self.room.price_per_night
         super().save(*args, **kwargs)

     def __str__(self):
         return f"Reservation for {self.guest} in Room {self.room.number}"

     class Meta:
         verbose_name = "Rezerwacja"
         verbose_name_plural = "Rezerwacje"


class SocialApp(models.Model):
    PROVIDERS = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('github', 'GitHub'),
    ]

    provider = models.CharField(max_length=50, choices=PROVIDERS)
    name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    sites = models.ManyToManyField(Site, related_name='social_apps')

    class Meta:
        unique_together = ('provider', 'client_id')
        verbose_name = "Aplikacja społecznościowa"
        verbose_name_plural = "Aplikacje społecznościowe"

    def __str__(self):
        return f"{self.name} ({self.provider})"




#
#def room_list(request):
#     rooms = Room.objects.all()
#     return render(request, 'hotel/room_list.html', {'rooms': rooms})
#
#def room_detail(request, pk):
#     room = get_object_or_404(Room, pk=pk)
#     return render(request, 'hotel/room_detail.html', {'room': room})
#
#def make_reservation(request, pk):
#     room = get_object_or_404(Room, pk=pk)
#     if request.method == 'POST':
#         form = ReservationForm(request.POST)
#         if form.is_valid():
#             reservation = form.save(commit=False)
#             reservation.room = room
#             reservation.save()
#             return render(request, 'hotel/reservation_success.html', {'reservation': reservation})
#     else:
#         form = ReservationForm()
#     return render(request, 'hotel/make_reservation.html', {'room': room, 'form': form})


