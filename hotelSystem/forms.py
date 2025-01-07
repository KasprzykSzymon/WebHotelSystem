from django import forms
from django.contrib.auth.models import User
from .models import Reservation, Guest


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

class ReservationForm(forms.ModelForm):
    guest = forms.ModelChoiceField(queryset=Guest.objects.all(), required=True)

    class Meta:
        model = Reservation
        fields = ['guest', 'check_in_date', 'check_out_date']
