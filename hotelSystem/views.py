from .last_minute import generate_last_minute_offer
from django.contrib.auth import logout, authenticate, login
from .forms import UserProfileForm, EventSearchForm
from hotelSystem.logic.last_minute import generate_last_minute_offer
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Room, Reservation, Payment, Event
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
import requests
import json
import hmac
import hashlib
import base64
from dotenv import load_dotenv
import os
from .payment_helpers import new_payment, check_payment

def home_page_view(request):
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    adults = request.GET.get('adults', 1)
    children = request.GET.get('children', 0)

    today = datetime.today().date()
    error_message = None

    if arrival_date and departure_date:
        try:
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()

            if arrival_date_obj < today:
                error_message = "Data przyjazdu nie może być wcześniejsza niż dzisiejsza data."
            elif departure_date_obj <= arrival_date_obj:
                error_message = "Data odjazdu nie może być wcześniejsza niż data przyjazdu."
        except ValueError:
            error_message = "Podano nieprawidłowy format daty."

    if not error_message and arrival_date and departure_date:
        query_params = f"?arrival_date={arrival_date}&departure_date={departure_date}&adults={adults}&children={children}"
        return HttpResponseRedirect(reverse('search_room') + query_params)

    if error_message:
        messages.error(request, error_message)

    context = {
        'range_10': range(11),
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
        'search': reverse('search_room'),
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'adults': adults,
        'children': children
    }
    return render(request, 'home_page.html', context)

def last_minute_view(request):
    days_to_last_minute = 4
    max_discount = 30
    offers = generate_last_minute_offer(days_to_last_minute=days_to_last_minute, max_discount=max_discount)
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

def search_room_view(request):
    rooms = Room.objects.all()
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    adults = request.GET.get('adults', '0')
    children = request.GET.get('children', '0')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_order = request.GET.get('sort_order')
    error_message = None

    try:
        total_guests = int(adults) + int(children)
    except ValueError:
        total_guests = 0

    if arrival_date and departure_date:
        try:
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
            today = datetime.today().date()

            if arrival_date_obj < today:
                error_message = "Data przyjazdu nie może być wcześniejsza niż dzisiejsza data."
                rooms = Room.objects.none()
            elif departure_date_obj <= arrival_date_obj:
                error_message = "Data odjazdu nie może być wcześniejsza niż data przyjazdu."
                rooms = Room.objects.none()
        except ValueError:
            error_message = "Podano nieprawidłowy format daty."
            rooms = Room.objects.none()

    if not error_message:
        if total_guests > 0:
            rooms = rooms.filter(capacity__gte=total_guests)
        if room_type and room_type != 'None':
            rooms = rooms.filter(room_type=room_type)
        if min_price and min_price.isdigit():
            rooms = rooms.filter(price_per_night__gte=float(min_price))
        if max_price and max_price.isdigit():
            rooms = rooms.filter(price_per_night__lte=float(max_price))

        if sort_order == 'desc':
            rooms = rooms.order_by('-price_per_night')
        elif sort_order == 'asc':
            rooms = rooms.order_by('price_per_night')

        if not rooms.exists():
            error_message = "Nie znaleziono pokoi spełniających podane kryteria."

    context = {
        'rooms': rooms,
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'adults': adults,
        'children': children,
        'room_type': room_type,
        'min_price': min_price,
        'max_price': max_price,
        'sort_order': sort_order,
        'error_message': error_message
    }
    return render(request, 'search_room.html', context)

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
            user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
            user.save()


            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, 'Rejestracja zakończona sukcesem. Zostałeś zalogowany.')
            return redirect('home_page')
        except Exception as e:
            messages.error(request, f'Błąd rejestracji: {e}')
    return render(request, 'register.html')

@login_required
def profile_view(request):
    # Pobieramy rezerwacje użytkownika
    reservations = Reservation.objects.filter(user=request.user).select_related('room', 'payment')

    # Przygotowanie danych rezerwacji
    reservation_details = [
        {
            'id': reservation.id,
            'room_number': reservation.room.number,
            'check_in_date': reservation.check_in_date,
            'check_out_date': reservation.check_out_date,
            'total_amount': (reservation.check_out_date - reservation.check_in_date).days * reservation.room.price_per_night,
            'paynow_id': reservation.payment.paynow_id if reservation.payment else "Brak płatności",
            'status': reservation.payment.status if reservation.payment else "Brak statusu",
            'email': reservation.user.email,
        }
        for reservation in reservations
    ]

    # Pobieramy wydarzenia (Event) z bazy danych
    events = Event.objects.all()

    event_details = [
        {
            'id': event.id,
            'name': event.name,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'description': event.description,
        }
        for event in events
    ]

    # Pobieramy reservation_id i event_id z URL (jeśli istnieją)
    reservation_id = request.GET.get('reservation_id')
    event_id = request.GET.get('event_id')  # Poprawiony sposób dostępu do parametru

    reservation_detail = None
    event_detail = None

    # Jeżeli mamy reservation_id, pobieramy szczegóły tej rezerwacji
    if reservation_id:
        reservation_detail = next((r for r in reservation_details if r['id'] == int(reservation_id)), None)

    # Jeżeli mamy event_id, pobieramy szczegóły tego wydarzenia
    if event_id:
        event_detail = next((e for e in event_details if e['id'] == int(event_id)), None)

    # Renderujemy szablon
    return render(request, 'profile.html', {
        'user': request.user,
        'reservations': reservation_details,
        'reservation_detail': reservation_detail,  # Przekazujemy szczegóły wybranej rezerwacji
        'event': event_detail,  # Szczegóły wybranego wydarzenia
        'event_details': event_details,  # Lista wszystkich wydarzeń
    })


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

from datetime import datetime

from datetime import datetime

from datetime import datetime
from django.shortcuts import render, get_object_or_404

#@login_required(login_url='sign_in')
def room_detail(request, pk):
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    room = get_object_or_404(Room, pk=pk)
    error_message = None
    total_price = None
    number_of_nights = 0

    # Calculate price and number of nights if dates are provided
    if arrival_date and departure_date:
        try:
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d').date()
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()

            if departure_date_obj <= arrival_date_obj:
                error_message = "Data odjazdu nie może być wcześniejsza niż data przyjazdu."
            else:
                # Calculate the number of nights
                number_of_nights = (departure_date_obj - arrival_date_obj).days
                # Calculate total price for the stay
                total_price = room.price_per_night * number_of_nights
        except ValueError:
            error_message = "Podano nieprawidłowy format daty."

    # Prepare information about the beds and their count
    single_beds_text = ''
    double_beds_text = ''

    if room.single_bed_count > 0:
        if room.single_bed_count == 1:
            single_beds_text = "1 łóżko pojedyncze"
        elif room.single_bed_count in [2, 3, 4]:
            single_beds_text = f"{room.single_bed_count} łóżka pojedyncze"
        else:
            single_beds_text = f"{room.single_bed_count} łóżek pojedynczych"

    if room.double_bed_count > 0:
        if room.double_bed_count == 1:
            double_beds_text = "1 łóżko podwójne"
        elif room.double_bed_count in [2, 3, 4]:
            double_beds_text = f"{room.double_bed_count} łóżka podwójne"
        else:
            double_beds_text = f"{room.double_bed_count} łóżek podwójnych"

    # Prepare bed icons
    single_bed_icons = ["<img src='{% static 'icons/single-bed.png' %}' alt='Single bed'>" for _ in range(room.single_bed_count)]
    double_bed_icons = ["<img src='{% static 'icons/double-bed.png' %}' alt='Double bed'>" for _ in range(room.double_bed_count)]

    context = {
        'room': room,
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'error_message': error_message,
        'number_of_nights': number_of_nights,
        'total_price': total_price,
        'single_beds_text': single_beds_text,
        'double_beds_text': double_beds_text,
        'single_beds': single_bed_icons,
        'double_beds': double_bed_icons,
    }
    print(room, arrival_date, departure_date, request.user)
    return render(request, 'room_detail.html', context)

@login_required(login_url='sign_in')
def place_order(request):
    print(request.POST)
    room_id = int(request.POST['room_id'])
    arrival_date_obj = datetime.strptime(request.POST['arrival_date'], '%Y-%m-%d').date()
    departure_date_obj = datetime.strptime(request.POST['departure_date'], '%Y-%m-%d').date()
    room_id = int(request.POST['room_id'])
    desc = request.POST['item_name']
    room = Room.objects.get(id=room_id)
    time = (departure_date_obj - arrival_date_obj).days
    print(time)
    cost = time * room.price_per_night
    cost = int(cost*100)
    payment = Payment()
    payment.amount=cost
    payment.save()
    reservation = Reservation()
    reservation.room=room
    print("USER", request.user)
    reservation.user = request.user
    reservation.check_in_date = arrival_date_obj
    reservation.check_out_date = departure_date_obj
    reservation.total_price = cost
    reservation.payment = payment
    reservation.save()

    
    paynow = new_payment({
        "amount": cost,
        "description": desc,
        "externalId": str(payment.id),
        "buyer": {
            "email": request.user.email,
            "phone": {
                "prefix": "+48",
                "number": "112112112"
            }
        },
        "continueUrl": f"http://127.0.0.1:8000/payment_confirmation?reservation={str(reservation.id)}"
    }, str(payment.id))
    payment.last_response = json.dumps(paynow)
    payment.status = paynow['status']
    payment.paynow_id = paynow['paymentId']
    payment.redirect_url = paynow['redirectUrl']
    payment.last_update = datetime.now()
    payment.save()
    print(paynow)
    return HttpResponseRedirect(paynow['redirectUrl'])


def order_confirmation(request):
    print(request.GET['reservation'])
    reservation_id = int(request.GET['reservation'])
    reservation = Reservation.objects.get(id=reservation_id)

      # Obliczanie liczby nocy
    number_of_nights = (reservation.check_out_date - reservation.check_in_date).days

    # Obliczanie całkowitej kwoty
    total_amount = reservation.room.price_per_night * number_of_nights

    # Inne obliczenia związane z płatnością
    payment = reservation.payment
    check = check_payment(payment.paynow_id)
    payment.status = check['status']
    payment.last_update = datetime.now()
    payment.save()

    if check['status'] != "CONFIRMED":
        return render(request, "payment_cancel.html")

    context = {
        "reservation": reservation,
        "total_amount": total_amount  # Przekazujemy całkowitą kwotę do szablonu
    }

    return render(request, 'payment_confirmation.html', context)

def news_view(request):
    events = None
    success_message = None
    
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            # Zamiana dat na obiekt typu datetime
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Filtrowanie wydarzeń na podstawie nakładających się dat
            events = Event.objects.filter(
                start_date__lte=end_date,  # Jeśli początek wydarzenia jest przed końcem zakresu
                end_date__gte=start_date   # Jeśli koniec wydarzenia jest po rozpoczęciu zakresu
            )

            # Sprawdzanie czy są wyniki
            if not events:
                success_message = "Brak wydarzeń w tym zakresie dat."

    return render(request, 'news.html', {'events': events, 'success_message': success_message})

def rezerwacja_view(request, event_id):
    # Pobieramy konkretne wydarzenie na podstawie event_id
    event = get_object_or_404(Event, id=event_id)
    
    # Przekazujemy wydarzenie do szablonu
    return render(request, 'rezerwacja.html', {'event': event})