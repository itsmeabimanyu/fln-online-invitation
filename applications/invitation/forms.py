from django import forms
from django.forms import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.validators import MinValueValidator
from .models import Event, Participant, InvitationStyle

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["image", "event_name", "description", "location", "maps_location", "from_event_date", "to_event_date" ]
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'id': 'imageInput',  # ID untuk input gambar
                'onchange': 'previewImage(event)',  # Menambahkan event onchange
            }),
            'event_name': forms.Textarea(attrs={'rows': 2}),
            'from_event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'to_event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'location': forms.Textarea(attrs={'rows': 2}),  # Batasi textarea menjadi 2 baris
            'maps_location': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'maps_location': 'Maps location (optional)', 
            'description': 'Description (optional)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control parsley-error'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

            # Add specific class for 'unit' field if it exists
            '''if field_name == 'description':
                field.widget.attrs.update({'class': 'form-control', "rows":"1"})'''

            """if field_name in ['name']:
                field.widget.attrs.update({'style': 'text-transform: uppercase;'})

            '''if field_name in ['warehouse']:
                field.widget.attrs.update({'class': 'basic form-control'})'''

            # Optionally, add other attributes like autocomplete="off"
            field.widget.attrs.update({'autocomplete': 'off'})

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ['name']:
            if field_name in cleaned_data and cleaned_data[field_name]:
                cleaned_data[field_name] = cleaned_data[field_name].upper()
        return cleaned_data"""
            
class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["organization", "guest_name", "email" ]

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
            'class': 'form-control',
            'placeholder': 'Enter greeting title'
        }),
        initial='You Are Invited!'  # Set default value here
    )
    
    greeting_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter greeting description',
            'rows': 3, 'cols': 50
        }),
        initial='It is our pleasure to invite you to join us for a special occasion.'  # Set default value here
    )

    appreciation_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
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
            'enable_dark_mode'
        ]
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file'}),
            'appreciation_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file'}),
            # 'set_as_background': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'enable_dark_mode': 'Enable Dark Mode?',
        }
        help_texts = {
            'greeting_description': 'Please provide a description for the greeting message.',
        }
