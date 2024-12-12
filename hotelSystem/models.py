from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from datetime import date, datetime
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
    capacity = models.IntegerField(default=1)
    single_bed_count = models.IntegerField(default=0)
    double_bed_count = models.IntegerField(default=0)

    def discounted_price(self):
        """Oblicza cenę po zniżce, zaokrągloną do dwóch miejsc po przecinku."""
        return self.price_per_night * (1 - self.last_minute_discount / 100)

    def save(self, *args, **kwargs):
        """Ustawia pojemność na podstawie typu pokoju."""
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

class Payment(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.TextField(null=True)
    amount = models.IntegerField()
    paynow_id = models.TextField(null=True)
    redirect_url = models.TextField(null=True)
    request = models.TextField(null=True)
    last_response = models.TextField(null=True)
    last_update = models.DateTimeField(auto_now_add=True)

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow user to be null
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, null=True, blank=True)

    def is_in_last_minute_period(self, threshold_date):
        return threshold_date >= self.check_in_date >= date.today()

    def save(self, *args, **kwargs):
        if self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            if nights > 0:
                self.total_price = round(nights * self.room.discounted_price(), 2)
        else:
            raise ValueError("Brak daty przyjazdu lub odjazdu.")
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Reservation for {self.guest} in Room {self.room.number}"

    class Meta:
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"

