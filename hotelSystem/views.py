from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserProfileForm  
from django.contrib.auth.decorators import login_required

def home_page(request):
    # Łączenie obu słowników w jeden
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
        'images': [
            {"id": "zdj1", "src": "images/Gory.jpg", "alt": "Góry Świętokrzyskie", "desc": "Wspaniałe widoki Gór Świętokrzyskich w hotelu Scyzoryk."},
            {"id": "zdj2", "src": "images/Kielce.jpg", "alt": "Kielce", "desc": "Odwiedź nasze miasto Kielce i ciesz się jego atrakcjami."},
            {"id": "zdj3", "src": "images/Hotel.jpg", "alt": "Hotel", "desc": "Oferujemy spotkania biznesowe dla firm!"}
        ],
        'hotel_location': {
            'lat': 50.8882347,  # Szerokość geograficzna
            'lng': 20.8720543   # Długość geograficzna
        },
        'search' : "{% url 'search_room' %}"
    }
    return render(request, 'home_page.html', context)

def last_minute(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'last_minute.html', context)

def news(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'news.html', context)


def contact(request):
    return render(request, 'contact.html')

def sign_in(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'sign_in.html', context)

def search_room(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'search_room.html', context)

def register(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'register.html', context)

def profile(request):
    context = {
        'range_10': range(0, 11),
        'range_10x': range(1, 11),
    }
    return render(request, 'profile.html', context)

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})