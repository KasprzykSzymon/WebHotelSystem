def generate_last_minute_offer(days_to_last_minute, max_discount):
    """
    Generuje oferty last minute.
    :param days_to_last_minute: Liczba dni przed terminem, które kwalifikują ofertę jako last minute.
    :param max_discount: Maksymalny procent zniżki.
    """
    from datetime import date, timedelta
    from hotelSystem.models import Room, Reservation
    from decimal import Decimal

    today = date.today()

    # Pobieranie pokoi z ich najbliższą rezerwacją
    reserved_rooms = Reservation.objects.filter(check_in_date__gte=today).values_list('room_id', 'check_in_date')
    room_to_reservation = {room_id: check_in_date for room_id, check_in_date in reserved_rooms}

    # Pobieranie wszystkich pokoi
    all_rooms = Room.objects.all()

    offers = []
    for room in all_rooms:


        # Sprawdź, czy pokój ma najbliższą rezerwację
        nearest_reservation_date = room_to_reservation.get(room.id)

        # Pomijamy pokoje z rezerwacją zaczynającą się dzisiaj lub wcześniej
        if nearest_reservation_date and nearest_reservation_date <= today:
            continue

        # Jeśli pokój nie ma rezerwacji, ustaw jego dostępność na "brak rezerwacji w przyszłości"
        if not nearest_reservation_date:
            continue  # Pokój nie spełnia warunków last minute

        # Oblicz liczbę dni do najbliższej rezerwacji
        days_until_reservation = (nearest_reservation_date - today).days
        if days_until_reservation > days_to_last_minute:
            continue  # Wyklucz pokój, jeśli nie spełnia warunku last minute

        available_days = days_until_reservation
        availability_end_date = nearest_reservation_date  # Dzień przed rezerwacją

        # Oblicz dynamiczną zniżkę
        base_discount = 10  # Podstawowa zniżka
        additional_discount_per_day = 2  # Dodatkowe % za dzień
        calculated_discount = base_discount + additional_discount_per_day * available_days

        # Ograniczenie zniżki do max_discount
        discount = min(calculated_discount, max_discount)

        # Oblicz cenę po zniżce
        original_price = Decimal(room.price_per_night * available_days)  # Konwersja na Decimal
        discounted_price = original_price * (Decimal(1) - Decimal(discount) / Decimal(100))
        # Pobierz wszystkie obrazy pokoju
        room_images = room.images.all()
        image_urls = [image.image.url for image in room_images]  # Lista URL obrazów

        # Dodaj pokój do ofert
        offers.append({
            'room': room,
            'original_price': round(original_price, 2),
            'total_price': round(discounted_price, 2),
            'discount': round(discount, 2),  # Zaokrąglona wartość zniżki
            'available_days': available_days,
            'arrival_date': today,
            'availability_end_date': availability_end_date,
            'today': today,
            'image_urls': image_urls,  # Lista URL obrazów

        })

    return offers