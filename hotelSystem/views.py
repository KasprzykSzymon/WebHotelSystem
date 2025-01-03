from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserProfileForm  
from django.contrib.auth.decorators import login_required
from hotelSystem.logic.last_minute import generate_last_minute_offer
from datetime import datetime
from django.contrib import messages

def home_page_view(request):
    error_message = None
    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')

    print(f"Arrival Date: {arrival_date}, Departure Date: {departure_date}")

    if arrival_date and departure_date:
        try:
            arrival_date_obj = datetime.strptime(arrival_date, '%Y-%m-%d')
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d')

            print(f"Parsed Dates: Arrival: {arrival_date_obj}, Departure: {departure_date_obj}")

            if departure_date_obj < arrival_date_obj:
                error_message = "Data odjazdu nie może być wcześniejsza niż data przyjazdu."
        except ValueError as e:
            error_message = f"Podano nieprawidłowy format daty: {e}"
            print(f"ValueError: {e}")

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
        'error_message': error_message,
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

    if request.user.is_authenticated:
        return redirect('home_page') 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_page')  
        else:
            messages.error(request, 'Błędny login lub hasło.')

    return render(request, 'sign_in.html')


def search_room_view(request):


    arrival_date = request.GET.get('arrival_date')
    departure_date = request.GET.get('departure_date')
    adults = request.GET.get('adults')
    children = request.GET.get('children')


    return render(request, 'search_room.html', {
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'adults': adults,
        'children': children,
    })

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

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

def profile_view(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'profile.html', context)

def logout_view(request):
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