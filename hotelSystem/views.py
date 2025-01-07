from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserProfileForm  
from django.contrib.auth.decorators import login_required
from hotelSystem.logic.last_minute import generate_last_minute_offer
import paypalrestsdk
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from paypalrestsdk import Payment
from .models import Room, Reservation
from django.urls import reverse
from django.contrib.auth.models import User


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
    offers = generate_last_minute_offer(days_to_last_minute=7, max_discount=30)

    context = {
        'offers': offers,
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    days_to_last_minute = 5
    max_discount = 20
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
    reservations = Reservation.objects.filter(user=request.user).select_related('room')

    reservation_details = [
        {
            'id': reservation.id,
            'owner': f"{reservation.user.first_name} {reservation.user.last_name}",
            'room_name': reservation.room.name,
            'check_in_date': reservation.check_in_date,
            'check_out_date': reservation.check_out_date,
            'total_amount': (reservation.check_out_date - reservation.check_in_date).days * reservation.room.price
        }
        for reservation in reservations
    ]

    return render(request, 'profile.html', {
        'user': request.user,
        'reservations': reservation_details
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

@login_required(login_url='sign_in')
def room_detail(request, pk):
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    adults = request.GET.get('adults')
    children = request.GET.get('children')
    room_type = request.GET.get('room_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_order = request.GET.get('sort_order')

    room = get_object_or_404(Room, pk=pk)
    error_message = None
    total_price = None
    number_of_nights = 0
    total_beds = []

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
    return render(request, 'room_detail.html', context)



@login_required
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
    room = Room.objects.get(pk=pk)

    if request.method == "POST":
        # Wykonaj logikę płatności
        payment_successful = process_payment(request)  # Zastąp tym, co masz do obsługi płatności

        if payment_successful:
            # Tworzymy rezerwację
            reservation = Reservation.objects.create(
                user=request.user,
                room=room,
                check_in_date=request.POST['check_in_date'],
                check_out_date=request.POST['check_out_date']
            )
            # Przekierowanie do widoku potwierdzenia płatności
            return redirect('payment_confirmation', reservation_id=reservation.id)
        else:
            # Jeżeli płatność nie powiodła się
            messages.error(request, "Płatność nie powiodła się. Spróbuj ponownie.")
            return redirect('make_reservation', pk=pk)

    return render(request, 'room_detail.html', {'room': room})

# Konfiguracja PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "AY_xt2ZKCsnMSyBB3X_q_ffXxC1MmYQw8LWmktNBgacosS57spW2rRHp4q-hhs0QYX2HEu7iX-cIoYUl",
    "client_secret": "EOM8iMY97EtwuwGJkE2ZRm7nC1915fFkG-UTU7piQNnFG4bCEm52lT_GVmKe24jy4-x0fcweACMTE-1a"
})

@login_required(login_url='sign_in')
def process_payment(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('payment_success', args=[room_id])),
                "cancel_url": request.build_absolute_uri(reverse('payment_cancel'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": room.name,
                        "sku": str(room.id),
                        "price": f"{room.price:.2f}",  # Ensure the price is correctly formatted
                        "currency": "PLN",  # Ensure PLN is used as the currency
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{room.price:.2f}",  # Ensure the total amount is formatted correctly
                    "currency": "PLN"  # Ensure PLN is used as the currency
                },
                "description": f"Rezerwacja pokoju: {room.name}"
            }]
        })

        logger = logging.getLogger(__name__)

        if not payment.create():
            logger.error(f"Payment creation failed: {payment.error}")
            return render(request, "payment_error.html", {"error": payment.error})

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    return redirect(approval_url)
        else:
            return render(request, "payment_error.html", {"error": payment.error})
    return redirect('room_list')

@login_required(login_url='sign_in')
def payment_success(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Tworzenie rezerwacji w bazie danych
    reservation = Reservation.objects.create(
        user=request.user,
        room=room,
        check_in_date=request.session.get('check_in_date'),  # Można użyć sesji do przechowywania dat
        check_out_date=request.session.get('check_out_date'),  # Podobnie z datą wyjazdu
        total_amount=room.price  # Całkowita kwota płatności
    )

    # Zapisanie płatności w bazie danych
    reservation.payment_status = 'Completed'
    reservation.save()

    # Przekierowanie na stronę potwierdzenia
    return render(request, 'payment_confirmation.html', {'reservation': reservation})

@login_required(login_url='sign_in')
def payment_cancel(request):
    return render(request, 'payment_cancel.html', {'error': "Płatność została anulowana."})
@login_required
def payment_confirmation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    total_amount = (reservation.check_out_date - reservation.check_in_date).days * reservation.room.price

    return render(request, 'payment_confirmation.html', {
        'reservation': reservation,
        'total_amount': total_amount,
    })
