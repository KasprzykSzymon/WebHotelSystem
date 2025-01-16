from django.test import TestCase
from django.contrib.auth.models import User
from .models import Reservation, Room, Guest, Event, Payment
from django.utils import timezone
from django.core.exceptions import ValidationError


class ReservationModelTest(TestCase):
    """Test reservation model"""
    def setUp(self):
        # Create sample user, room, guest, and payment for the tests
        self.user = User.objects.create_user(username='natka', password='123')
        self.room = Room.objects.create(number="101", room_type="single", price_per_night=100.0)
        self.payment = Payment.objects.create(amount=300)
        self.guest = Guest.objects.create(username="guest1", first_name="John", last_name="Doe", email="guest1@example.com", phone_number="123456789")

    def test_create_reservation(self):
        """Create a reservation"""
        reservation = Reservation.objects.create(
            guest=self.guest.username,
            user=self.user,
            room=self.room,
            check_in_date=timezone.now().date(),
            check_out_date=timezone.now().date() + timezone.timedelta(days=3),
            payment=self.payment
        )

        self.assertEqual(reservation.guest, "guest1")
        self.assertTrue(reservation.check_in_date <= reservation.check_out_date)
        self.assertEqual(reservation.user.username, "natka")
        self.assertEqual(reservation.total_price, 300.0)

    def test_check_out_in_the_future(self):
        """Test that a reservation with check-out date before check-in date raises a validation error."""
        reservation = Reservation.objects.create(
            guest="guest2",
            user=self.user,
            room=self.room,
            check_in_date=timezone.now().date(),
            check_out_date=timezone.now().date() + timezone.timedelta(days=-1)
        )

        with self.assertRaises(ValidationError):
            reservation.full_clean()


    def test_room_availability(self):
        """Test if the room is available for a certain date range"""
        reservation = Reservation.objects.create(
            guest="guest4",
            user=self.user,
            room=self.room,
            check_in_date=timezone.now().date(),
            check_out_date=timezone.now().date() + timezone.timedelta(days=2),
            payment=self.payment
        )

        # Check room availability for overlapping reservation
        is_available = self.room.is_available(timezone.now().date(), timezone.now().date() + timezone.timedelta(days=1))
        self.assertFalse(is_available)

        # Check room availability for non-overlapping dates
        is_available = self.room.is_available(timezone.now().date() + timezone.timedelta(days=3), timezone.now().date() + timezone.timedelta(days=4))
        self.assertTrue(is_available)


    def test_event_object(self):
        """Test creating an event object and assigning a user."""
        event = Event.objects.create(
            name="event_name",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=2),
            description="my_description_for_event",
        )
        # Assign the user to the event
        event.users.set([self.user])
        # Assertions
        self.assertEqual(event.name, "event_name")
        self.assertEqual(event.description, "my_description_for_event")
        self.assertTrue(event.start_date <= event.end_date)
        self.assertEqual(event.users.first().username, self.user.username)

class PaymentModelTest(TestCase):
    """Test Payment model"""
    def setUp(self):
        """Creates a sample Payment instance for testing."""
        self.payment = Payment.objects.create(
            status="pending",
            amount=100,
            paynow_id="123456",
            redirect_url="https://example.com/redirect",
            request="Sample request data",
            last_response="Sample response data"
        )

    def test_payment_creation(self):
        """Tests if the Payment object is created correctly."""
        self.assertIsInstance(self.payment, Payment)
        self.assertEqual(self.payment.status, "pending")
        self.assertEqual(self.payment.amount, 100)
        self.assertEqual(self.payment.paynow_id, "123456")
        self.assertEqual(self.payment.redirect_url, "https://example.com/redirect")
        self.assertEqual(self.payment.request, "Sample request data")
        self.assertEqual(self.payment.last_response, "Sample response data")

    def test_auto_now_add_fields(self):
        """Tests if the creation_date and last_update fields are set automatically."""
        self.assertIsNotNone(self.payment.creation_date)
        self.assertIsNotNone(self.payment.last_update)
        self.assertAlmostEqual(self.payment.creation_date, timezone.now(), delta=timezone.timedelta(seconds=1))
        self.assertAlmostEqual(self.payment.last_update, timezone.now(), delta=timezone.timedelta(seconds=1))

    def test_update_payment_status(self):
        """Tests if the payment status can be updated correctly."""
        self.payment.status = "completed"
        self.payment.save()
        updated_payment = Payment.objects.get(id=self.payment.id)
        self.assertEqual(updated_payment.status, "completed")

class GuestModelTest(TestCase):
    """Test quest model"""
    def setUp(self):
        """Creates a sample Guest instance for testing."""
        self.guest = Guest.objects.create(
            username="jdoe",
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            phone_number="123456789"
        )

    def test_guest_creation(self):
        """Tests if the Guest object is created correctly."""
        self.assertIsInstance(self.guest, Guest)
        self.assertEqual(self.guest.username, "jdoe")
        self.assertEqual(self.guest.first_name, "John")
        self.assertEqual(self.guest.last_name, "Doe")
        self.assertEqual(self.guest.email, "johndoe@example.com")
        self.assertEqual(self.guest.phone_number, "123456789")

    def test_guest_str_method(self):
        """Tests the __str__ method of the Guest object."""
        self.assertEqual(str(self.guest), "John Doe")

    def test_unique_email_constraint(self):
        """Tests if the unique constraint on email works correctly."""
        with self.assertRaises(Exception):
            Guest.objects.create(
                username="anotheruser",
                first_name="Jane",
                last_name="Doe",
                email="johndoe@example.com",  # Duplicate email
                phone_number="987654321"
            )


class RoomModelTest(TestCase):
    """Test room model"""
    def setUp(self):
        """Set up test data for the Room model."""
        self.room1 = Room.objects.create(
            number='101',
            room_type='single',
            price_per_night=100.00,
            last_minute_discount=10.00,
            single_bed_count=1,
            double_bed_count=0
        )

        self.room2 = Room.objects.create(
            number='102',
            room_type='suite',
            price_per_night=300.00,
            last_minute_discount=5.00,
            single_bed_count=1,
            double_bed_count=1
        )


    def test_room_creation(self):
        """Test if the Room is created correctly."""
        room = Room.objects.get(number='101')
        self.assertEqual(room.number, '101')
        self.assertEqual(room.room_type, 'single')
        self.assertEqual(room.price_per_night, 100.00)
        self.assertEqual(room.capacity, 1)  # Based on 'single' room type

    def test_room_capacity_based_on_type(self):
        """Test if the capacity is set correctly based on room type."""
        room1 = Room.objects.get(number='101')
        room2 = Room.objects.get(number='102')

        self.assertEqual(room1.capacity, 1)  # 'single' room type
        self.assertEqual(room2.capacity, 4)  # 'suite' room type

    def test_discounted_price(self):
        """Test if the discounted price is calculated correctly."""
        room = Room.objects.get(number='101')
        expected_discounted_price = 100.00 * (1 - 10 / 100)  # 10% discount
        self.assertEqual(room.discounted_price(), expected_discounted_price)

    def test_room_str_method(self):
        """Test the __str__ method for the Room model."""
        room = Room.objects.get(number='101')
        self.assertEqual\
        (str(room), 'Room 101 (Single)')

