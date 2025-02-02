from django import forms
from django.forms import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.validators import MinValueValidator
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event_date", "event_name", "location", "description"]
        widgets = {
            'event_name': forms.Textarea(attrs={'rows': 2}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'location': forms.Textarea(attrs={'rows': 2}),  # Batasi textarea menjadi 2 baris
            'description': forms.Textarea(attrs={'rows': 3}),
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