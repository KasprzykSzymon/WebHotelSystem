from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .forms import UserProfileForm
from hotelSystem.logic.last_minute import generate_last_minute_offer
from datetime import datetime
from paypalrestsdk import Payment
from .models import Room, Reservation
import paypalrestsdk
import uuid
import requests
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.contrib import messages
from datetime import datetime

from django.contrib import messages
from datetime import datetime

from django.contrib import messages
from datetime import datetime

def home_page_view(request):
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')

    print(f"Arrival Date: {arrival_date}, Departure Date: {departure_date}")

    today = datetime.today().date()  # dzisiejsza data

    if arrival_date and departure_date:
        try:
            # Parsowanie dat
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()

            print(f"Parsed Dates: Arrival: {arrival_date_obj}, Departure: {departure_date_obj}")

            # Sprawdzanie, czy data przyjazdu nie jest wcześniejsza niż dzisiejsza data
            if arrival_date_obj < today:
                messages.error(request, "Data przyjazdu nie może być wcześniejsza niż dzisiejsza data.")
            
            # Sprawdzanie, czy data odjazdu nie jest wcześniejsza niż data przyjazdu
            elif departure_date_obj < arrival_date_obj:
                messages.error(request, "Data odjazdu nie może być wcześniejsza niż data przyjazdu.")

        except ValueError as e:
            messages.error(request, f"Podano nieprawidłowy format daty: {e}")
            print(f"ValueError: {e}")

    # Kontekst przekazywany do szablonu
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
        'images': [
            {"id": "zdj1", "src": "images/Gory.jpg", "alt": "Góry Świętokrzyskie", "desc": "Wspaniałe widoki Gór Świętokrzyskich w hotelu Scyzoryk."},
            {"id": "zdj2", "src": "images/Kielce.jpg", "alt": "Kielce", "desc": "Odwiedź nasze miasto Kielce i ciesz się jego atrakcjami."},
            {"id": "zdj3", "src": "images/Hotel.jpg", "alt": "Hotel", "desc": "Oferujemy spotkania biznesowe dla firm!"}
        ],
        'hotel_location': {
            'lat': 50.8882347,
            'lng': 20.8720543
            
        },
        'search': "{% url 'search_room' %}",
    }
    return render(request, 'home_page.html', context)



def last_minute_view(request):
    offers = generate_last_minute_offer(days_to_last_minute=5, max_discount=20)
    context = {
        'offers': offers,
        'range_10': range(0, 11),
        'range_10x': range(1, 11),

    }
    return render(request, 'last_minute.html', {'offers': offers})

def news_view(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'news.html', context)


def contact_view(request):
    return render(request, 'contact.html')

def sign_in_view(request):
    # Sprawdzenie, czy użytkownik jest już zalogowany
    if request.user.is_authenticated:
        messages.info(request, 'Jesteś już zalogowany.')  # Informacyjny komunikat
        return redirect('home_page')  # Przekierowanie na stronę główną

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentykacja użytkownika
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Witaj, {user.username}! Pomyślnie zalogowano.')  # Komunikat sukcesu
            return redirect('home_page')  # Przekierowanie na stronę główną
        else:
            messages.error(request, 'Błędny login lub hasło.')  # Komunikat o błędzie logowania

    # Wyświetlenie formularza logowania
    return render(request, 'sign_in.html')

from django.db.models import Q

def search_room_view(request):
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    adults = int(request.GET.get('adults', 0))
    children = int(request.GET.get('children', 0))
    total_guests = adults + children

    rooms = Room.objects.all()

    if arrival_date and departure_date:
        try:
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()

            if arrival_date_obj >= departure_date_obj:
                messages.error(request, "Data odjazdu musi być późniejsza niż data przyjazdu.")
            else:
                reserved_rooms = Reservation.objects.filter(
                    Q(check_in_date__lte=departure_date_obj, check_out_date__gte=arrival_date_obj)
                ).values_list('room_id', flat=True)

                # Filtracja dostępnych pokoi na podstawie liczby gości
                rooms = rooms.exclude(id__in=reserved_rooms).filter(capacity__gte=total_guests)

        except ValueError as e:
            messages.error(request, f"Nieprawidłowy format daty: {e}")

    return render(request, 'search_room.html', {
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'adults': adults,
        'children': children,
        'rooms': rooms,
    })



def register_view(request):
    if request.method == 'POST':

        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        birthdate = request.POST.get('birthdate')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            messages.error(request, 'Hasła nie są identyczne.')
            return render(request, 'register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Użytkownik o podanym adresie email już istnieje.')
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
            user.save()


            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, 'Rejestracja zakończona sukcesem. Zostałeś zalogowany.')
            return redirect('home_page')
        except Exception as e:
            messages.error(request, f'Błąd rejestracji: {e}')
    return render(request, 'register.html')

@login_required
def profile_view(request):
    reservations = Reservation.objects.filter(user=request.user)  # Pamiętaj o user
    return render(request, 'profile.html', {'reservations': reservations})

def logout_view(request):
    request.session.flush()
    logout(request)
    messages.success(request, "Pomyślnie wylogowano.")
    return redirect('sign_in')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'room_list.html', {'rooms': rooms})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'room_detail.html', {'room': room})

def make_reservation(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.room = room
            reservation.user = request.user  # przypisujemy zalogowanego użytkownika
            reservation.save()
            return render(request, 'reservation_success.html', {'reservation': reservation})
    else:
        form = ReservationForm()

    return render(request, 'make_reservation.html', {'room': room, 'form': form})

# Konfiguracja PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

def process_payment(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('payment_success')),
                "cancel_url": request.build_absolute_uri(reverse('payment_cancel'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": room.name,
                        "sku": str(room.id),
                        "price": str(room.price),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(room.price),
                    "currency": "USD"
                },
                "description": f"Rezerwacja pokoju: {room.name}"
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return redirect(approval_url)
        else:
            return render(request, "payment_error.html", {"error": payment.error})
    return redirect('room_list')

def payment_success(request):
    reservation_data = request.session.get('reservation_data')
    if reservation_data:
        Reservation.objects.create(**reservation_data)
    return render(request, "payment_success.html")

def payment_cancel(request):
    return render(request, "payment_cancel.html")
