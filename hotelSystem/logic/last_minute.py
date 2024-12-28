from datetime import date, timedelta
from hotelSystem.models import Room, Reservation
from decimal import Decimal

def generate_last_minute_offer(days_to_last_minute=0, max_discount=0):
    """
    Generuje oferty last minute.
    param days_to_last_minute: Liczba dni przed terminem, kóre kwalifikują ofertę jako last minute.
    param max_discount: Max procent zniżki.
    """


    today = date.today()
    last_minute_treshold =today + timedelta(days=days_to_last_minute)

    # Rezerwacje zaczynające się po okresie "last minute"
    reserved_rooms = Reservation.objects.filter(
        check_in_date__lte=last_minute_treshold, #rezerwacje do dnia threshold
        check_in_date__gte=today).values_list('room_id', flat=True) #tylko przyszle rezerwacje




    # Filtracja dostępnych pokoi
    available_rooms = Room.objects.filter(is_available=True).exclude(id__in=reserved_rooms)

    offers = []
    for room in available_rooms:
        # Oblicz dynamiczną zniżkę
        discount = min(max_discount, 10 + days_to_last_minute * 2)  # Modyfikacja logiki
        discount_decimal = Decimal(discount) / Decimal(100) #konwersja float na decimal
        discounted_price = room.price_per_night * (1 - discount_decimal)
        offers.append({
            'room': room,
            'original_price': room.price_per_night,
            'discounted_price': discounted_price,
            'discount': discount,
        })
    return offers