from datetime import date, timedelta
from .models import Room, Reservation

def generate_last_minute_offer(days_to_last_minute=7, max_discount=30):
        """

       Generuje oferty last minute.

        param days_to_last_minute: Liczba dni przed terminem, kóre kwalifikują ofertę jako last minute.
        param max_discount: Max procent zniżki.
        """


        today = date.today()
        reserved_rooms = Reservation.objects.filter(
        check_in_date__gte=today
        ).values_list('room_id', flat=True)

        # Filtracja dostępnych pokoi
        available_rooms = Room.objects.filter(is_available=True).exclude(id__in=reserved_rooms)

        offers = []
        for room in available_rooms:
            # Oblicz dynamiczną zniżkę
            discount = min(max_discount, 10 + days_to_last_minute * 2)  # Modyfikacja logiki
            discounted_price = room.price_per_night * (1 - discount / 100)
            offers.append({
                'room': room,
                'original_price': room.price_per_night,
                'discounted_price': discounted_price,
                'discount': discount,
            })
        return offers