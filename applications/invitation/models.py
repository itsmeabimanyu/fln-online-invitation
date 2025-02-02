from django.db import models
from django.core.validators import EmailValidator

# Event Model - As before, representing an event to which people or companies are invited
class Event(models.Model):
    event_name = models.TextField()
    event_date = models.DateTimeField()
    description = models.TextField()
    location = models.TextField()
    event_type = models.CharField(max_length=50)  # e.g., "Wedding", "Conference"
    # image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    def __str__(self):
        return self.event_name

class Organization(models.Model):
    # Informasi instansi
    name = models.CharField(max_length=255, verbose_name="Nama Instansi")
    address = models.TextField(blank=True, null=True, verbose_name="Alamat Instansi")
    email = models.EmailField(validators=[EmailValidator()], blank=True, null=True, verbose_name="Email Instansi")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor Telepon Instansi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    def __str__(self):
        return self.name

class Guest(models.Model):
    # Informasi tamu
    invitation = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="guests", verbose_name="Undangan")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Instansi")
    guest_name = models.CharField(max_length=255, verbose_name="Nama Tamu")
    guest_email = models.EmailField(validators=[EmailValidator()], verbose_name="Email Tamu")
    is_attending = models.BooleanField(default=False, verbose_name="Hadir?")
    additional_guests = models.PositiveIntegerField(default=0, verbose_name="Tamu Tambahan")
    special_requests = models.TextField(blank=True, null=True, verbose_name="Permintaan Khusus")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")

    def __str__(self):
        return f"{self.guest_name} ({'Hadir' if self.is_attending else 'Tidak Hadir'})"

    
