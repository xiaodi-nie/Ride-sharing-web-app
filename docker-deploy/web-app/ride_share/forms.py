from django import forms
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
import re


def email_check(email):
    pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
    return re.match(pattern, email)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    email = forms.EmailField(label='Email', )
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    # Use clean methods to define custom validation rules

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 6:
            raise forms.ValidationError("Your username must be at least 6 characters long.")
        elif len(username) > 50:
            raise forms.ValidationError("Your username is too long.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your username already exists.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email_check(email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("Your email already exists.")
        else:
            raise forms.ValidationError("Please enter a valid email.")

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    # Use clean methods to define custom validation rules

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if email_check(username):
            filter_result = User.objects.filter(email__exact=username)
            if not filter_result:
                raise forms.ValidationError("This email does not exist.")
        else:
            filter_result = User.objects.filter(username__exact=username)
            if not filter_result:
                raise forms.ValidationError("This username does not exist. Please register first.")

        return username


class ProfileForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=50, required=False)
    last_name = forms.CharField(label='Last Name', max_length=50, required=False)


class PwdChangeForm(forms.Form):
    old_password = forms.CharField(label='Old password', widget=forms.PasswordInput)

    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    # Use clean methods to define custom validation rules

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            raise forms.ValidationError("Your password is too short.")
        elif len(password1) > 20:
            raise forms.ValidationError("Your password is too long.")

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password mismatch. Please enter again.")

        return password2


class DriverRegistrationForm(forms.Form):
    vehicle_type = forms.ChoiceField(choices=[('sedan', 'Sedan'), ('suv', 'SUV')])
    plate_num = forms.CharField(label='Plate Number', )
    max_passenger = forms.IntegerField(label='Max Passenger')
    note = forms.CharField(label='Special Information:', required=False)


class RequestCarForm(forms.Form):
    # vehicle_type = forms.ChoiceField(choices=[('sedan', 'Sedan'), ('suv', 'SUV')])
    address = forms.CharField(label='address')
    passenger_num = forms.IntegerField(label='passenger_num')
    note = forms.CharField(label='note', required=False)
    time = forms.DateTimeField(label='time', input_formats=['%Y-%m-%d %H:%M', ],
                               help_text='Please input time as format: Year-Month-Day Hour:Minute')
    is_shareable = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], required=False)

    def clean_time(self):
        time = self.cleaned_data.get('time')
        if time - timezone.now() <= timedelta(seconds=0):
            print(timezone.now())
            print(time)
            raise forms.ValidationError("Time must be after the current time. Please enter again.")
        return time


class UpdateCurrentTripForm(forms.Form):
    address = forms.CharField(label='address')
    passenger_num = forms.IntegerField(label='passenger_num')
    note = forms.CharField(label='note', required=False)
    time = forms.DateTimeField(label='time', input_formats=['%Y-%m-%d %H:%M', ],
                               help_text='Please input time as format: Year-Month-Day Hour:Minute')
    is_shareable = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], required=False)


class ShareCarForm(forms.Form):
    address = forms.CharField(label='address')

    start_time = forms.DateTimeField(label='start_time', input_formats=['%Y-%m-%d %H:%M', ])
    final_time = forms.DateTimeField(label='final_time',
                                     input_formats=['%Y-%m-%d %H:%M', ],
                                     help_text='Please input time as format: Year-Month-Day Hour:Minute')

    # def clean_start_time(self):
    #     start_time = self.cleaned_data.get('start_time')
    #     final_time = self.cleaned_data.get('final_time')
    #     print(start_time)
    #     print(final_time)
    #     if final_time - start_time <= timedelta(minutes=1):
    #         raise forms.ValidationError("Times must be at lease 1 min apart. Please enter again.")
    #     if start_time - datetime.now() <= timedelta(seconds=0):
    #         raise forms.ValidationError("Time must be after the current time. Please enter again.")
    #     return start_time
    #
    # def clean_end_time(self):
    #     start_time = self.cleaned_data.get('start_time')
    #     final_time = self.cleaned_data.get('final_time')
    #     if final_time - start_time <= timedelta(minutes=1):
    #         raise forms.ValidationError("Times must be at lease 1 min apart. Please enter again.")
    #     if final_time - datetime.now() <= timedelta(seconds=0):
    #         raise forms.ValidationError("Time must be after the current time. Please enter again.")
    #     return final_time


class JoinRideForm(forms.Form):
    passenger_num = forms.IntegerField(label='passenger_num')
