from django import forms
from django.forms import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.validators import MinValueValidator
from .models import Event, Participant, InvitationStyle
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event_name", "description", "location", "maps_location", "from_event_date", "to_event_date", "quota_limitation", "image"]
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'id': 'imageInput',  # ID untuk input gambar
                'onchange': 'previewImage(event)',  # Menambahkan event onchange
            }),
            'maps_location': forms.TextInput(attrs={'placeholder': 'Enter link to maps location'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter event location'}),
            'event_name': forms.TextInput(attrs={'placeholder': 'Enter event name'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter event description'}),
            # 'from_event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            # 'to_event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'from_event_date': forms.DateTimeInput(attrs={'placeholder': 'Enter from event date'}),
            'to_event_date': forms.DateTimeInput(attrs={'placeholder': 'Enter to event date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control mt-2 parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control mt-2'})

            if field_name in ['from_event_date', 'to_event_date']:
                field.widget.attrs.update({'class': 'form-control datetime flatpickr-input'})

            field.widget.attrs.update({'autocomplete': 'off'})
            
class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["guest_name", "organization", "email" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control mt-2 parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control mt-2'})

            field.widget.attrs.update({'autocomplete': 'off'})

class ParticipantRegisterForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["organization", "guest_name", "email" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].widget.attrs.update({'placeholder': 'Enter your organization name'})
        self.fields['guest_name'].widget.attrs.update({'placeholder': 'Enter your name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})

        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control m-2 parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control m-2'})

class InvitationStyleForm(forms.ModelForm):
    greeting_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter greeting title'
        }),
        initial='You Are Invited!'  # Set default value here
    )

    greeting_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter greeting description',
            'rows': 3, 'cols': 50
        }),
        initial='It is our pleasure to invite you to join us for a special occasion.'  # Set default value here
    )

    appreciation_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter appreciation text',
            'rows': 3, 'cols': 50
        }),
        initial='Thank you for your response. You will now wait for further updates from us.'  # Set default value here
    )

    class Meta:
        model = InvitationStyle
        fields = [
            'greeting_title', 
            'greeting_description', 
            'image',
            'appreciation_image', 
            'appreciation_text', 
            # 'set_as_background', 
            'enable_dark_mode',
            'show_map_qrcode_on_invitation'
        ]
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'id': 'imageInput',  # ID untuk input gambar
                'onchange': 'previewImage(event)',  # Menambahkan event onchange
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control mt-2 parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control mt-2'})

            if field_name in ['enable_dark_mode', 'show_map_qrcode_on_invitation']:
                field.widget.attrs.update({'class': 'form-check mt-2 form-check-input'})

            field.widget.attrs.update({'autocomplete': 'off'})

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control mt-2 mb-2', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mt-2 mb-2', 'placeholder': 'Enter your password'})
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control mt-2 parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control mt-2'})

            field.widget.attrs.update({'autocomplete': 'off'})