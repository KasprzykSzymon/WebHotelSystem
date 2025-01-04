from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

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

from django.db import models

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('family', 'Family'),
        ('special', 'Special'),
        ('party', 'Party'),
        ('marriage', 'Marriage'),
        ('triple', 'Triple'),
        ('triple_marriage', 'Triple Marriage'),
    ]

    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    last_minute_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    capacity = models.IntegerField(default=1)  # Domyślna wartość

    def discounted_price(self):
        "Oblicza cene po znizce"
        return self.price_per_night * (1 - self.last_minute_discount / 100)

    def save(self, *args, **kwargs):
        # Mapowanie typu pokoju na pojemność
        type_to_capacity = {
            'single': 1,
            'double': 2,
            'suite': 4,
            'family': 5,
            'special': 8,
            'party': 10,
            'marriage': 2,
            'triple': 3,
            'triple_marriage': 3,
        }
        # Ustawienie capacity na podstawie room_type
        self.capacity = type_to_capacity.get(self.room_type, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room {self.number} ({self.get_room_type_display()})"

    class Meta:
        verbose_name = "Pokój"
        verbose_name_plural = "Pokoje"



class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')

    def __str__(self):
        return f"Image for Room {self.room.number}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow user to be null
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def is_in_last_minute_period(self, threshold_date):
        return threshold_date >= self.check_in_date >= date.today()

    def save(self, *args, **kwargs):
        nights = (self.check_out_date - self.check_in_date).days
        self.total_price = nights * self.room.discounted_price()  # Ensure this method is defined in the Room model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.guest} in Room {self.room.number}"

    class Meta:
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"

def make_reservation(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Create or update guest
            guest = form.cleaned_data['guest']
            # Create reservation
            reservation = form.save(commit=False)
            reservation.room = room
            reservation.user = request.user  # Przypisz aktualnie zalogowanego użytkownika
            reservation.save()

            messages.success(request, "Rezerwacja została pomyślnie dokonana.")
            return redirect('payment', pk=reservation.id)
    else:
        form = ReservationForm()

    return render(request, 'hotel/make_reservation.html', {'room': room, 'form': form})

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'hotel/room_list.html', {'rooms': rooms})
