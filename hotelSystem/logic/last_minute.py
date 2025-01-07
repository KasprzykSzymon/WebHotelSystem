from datetime import date, timedelta
from hotelSystem.models import Room, Reservation
from decimal import Decimal

def generate_last_minute_offer(days_to_last_minute, max_discount):
    """
    Generuje oferty last minute.
    :param days_to_last_minute: Liczba dni przed terminem, które kwalifikują ofertę jako last minute.
    :param max_discount: Maksymalny procent zniżki.
    """
    today = date.today()

    # Pobieranie pokoi z ich najbliższą rezerwacją
    reserved_rooms = Reservation.objects.filter(check_in_date__gte=today).values_list('room_id', 'check_in_date')
    room_to_reservation = {room_id: check_in_date for room_id, check_in_date in reserved_rooms}

    # Pobieranie wszystkich dostępnych pokoi
    available_rooms = Room.objects.filter(is_available=True)

    offers = []
    for room in available_rooms:
        # Sprawdź, czy pokój ma najbliższą rezerwację
        nearest_reservation_date = room_to_reservation.get(room.id)
        if nearest_reservation_date:
            days_until_reservation = (nearest_reservation_date - today).days
            if days_until_reservation > days_to_last_minute:
                continue  # Wyklucz pokój, jeśli nie spełnia warunku last minute
            available_days = days_until_reservation
            availability_end_date = nearest_reservation_date - timedelta(days=1)  # Dzień przed rezerwacją
        else:
            continue  # Wyklucz pokoje bez rezerwacji, bo nie spełniają warunku last minute

        # Oblicz dynamiczną zniżkę
        base_discount = 10  # Podstawowa zniżka
        additional_discount_per_day = 2  # Dodatkowe % za dzień
        calculated_discount = base_discount + additional_discount_per_day * available_days

        # Ograniczenie zniżki do max_discount
        discount = min(calculated_discount, max_discount)

        # Oblicz cenę po zniżce
        original_price = Decimal(room.price_per_night * available_days )  # Konwersja na Decimal
        discounted_price = original_price * (Decimal(1) - Decimal(discount) / Decimal(100))

        # Pobierz pierwszy obraz pokoju (lub None jeśli nie ma zdjec)
        room_image = room.images.first()

        # Dodaj pokój do ofert
        offers.append({
            'room': room,
            'original_price': round(original_price, 2),
            'discounted_price': round(discounted_price, 2),
            'discount': round(discount, 2),  # Zaokrąglona wartość zniżki
            'available_days': available_days,
            'availability_end_date': availability_end_date,
            'today': today,
            'image_url': room_image.image.url if room_image else None, #URL obrazu lub None
        })
    return offers
