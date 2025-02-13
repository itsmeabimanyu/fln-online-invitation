from django.db import models
from django.core.validators import EmailValidator
import uuid
from django.utils import timezone
from PIL import Image
from django.core.files.base import ContentFile
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
import string
import random
from django.contrib.auth import get_user_model

User = get_user_model() 

def generate_short_code():
    """Membuat kode pendek acak sepanjang 6 karakter."""
    length = 6
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choice(characters) for _ in range(length))

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.CharField(max_length=255, verbose_name="Event Name*")
    from_event_date = models.DateTimeField(verbose_name="From Event Date*")
    to_event_date = models.DateTimeField(verbose_name="To Event Date*")
    description = models.TextField(blank=True, null=True, verbose_name="Event Description")
    location = models.TextField(verbose_name="Location*")
    maps_location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Maps Location URL")
    # event_type = models.CharField(max_length=50)  # e.g., "Wedding", "Conference"
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Event Cover Image")
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    short_link = models.CharField(max_length=10, unique=True, verbose_name="Short Link")
    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invitations')

    def __str__(self):
        return self.event_name
    
    def clean(self):
        # Check if 'to_event_date' is earlier than 'from_event_date'
        if self.to_event_date < self.from_event_date:
            raise ValidationError("The 'To Event Date' cannot be earlier than the 'From Event Date'.")
        
        # Generate short_link jika belum ada
        if not self.short_link:
            self.short_link = generate_short_code()
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def close_event(self):
        self.is_active = False
        self.save()

    def open_event(self):
        self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        self.clean()
        if self.image:
            # Buka gambar yang diupload
            img = Image.open(self.image)
            
            # Jika gambar memiliki alpha channel (RGBA), konversi ke RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Cek ukuran gambar
            width, height = img.size
            
            # Resize atau padding untuk gambar lebih kecil dari 1280x720
            if width < 1280 or height < 720:
                # Menambahkan padding agar gambar menjadi 1280x720
                new_image = Image.new("RGB", (1280, 720), (255, 255, 255))  # Padding putih
                new_image.paste(img, ((1280 - width) // 2, (720 - height) // 2))  # Menempatkan gambar di tengah
                img = new_image  # Ganti gambar dengan padding
            else:
                # Resize menjadi 1280x720 untuk gambar yang lebih besar
                img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            
            # Simpan gambar dalam bentuk BytesIO untuk di-upload
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)
            
            # Buat InMemoryUploadedFile untuk gambar yang sudah diubah
            self.image = InMemoryUploadedFile(
                img_io, 
                field_name='image', 
                name=self.image.name, 
                content_type='image/jpeg', 
                size=img_io.tell(), 
                charset=None
            )
            
        super().save(*args, **kwargs)

class Participant(models.Model):
    # Informasi tamu
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invitation = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="guests", verbose_name="Undangan")
    # organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Instansi")
    organization = models.CharField(max_length=255, blank=True, null=True, verbose_name="Organization")
    guest_name = models.CharField(max_length=255, verbose_name="Name*")
    email = models.EmailField(validators=[EmailValidator()], blank=True, null=True, verbose_name="Email")
    is_attending = models.BooleanField(default=False, verbose_name="Is attending")
    attendance_time = models.DateTimeField(null=True, blank=True)
    # additional_guests = models.PositiveIntegerField(default=0, verbose_name="Tamu Tambahan")
    # special_requests = models.TextField(blank=True, null=True, verbose_name="Permintaan Khusus")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui Pada")
    is_approved = models.BooleanField(default=False, verbose_name="Approve?")
    approved_by =  models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_by')

    def __str__(self):
        return f"{self.guest_name}"
    
    class Meta:
        ordering = ['created_at']

    def approve_participant(self):
        self.is_approved = True
        self.save()

    def mark_attendance(self):
        self.is_attending = True
        self.attendance_time = timezone.now()  # Get the current time
        self.save()

class InvitationStyle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event", verbose_name="Event")
    greeting_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Greeting Title")
    greeting_description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Greeting Description")
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Image")
    appreciation_image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Appreciation Image")
    appreciation_text = models.CharField(max_length=255, null=True, blank=True, verbose_name="Appreciation Text")
    # set_as_background = models.BooleanField(default=False, verbose_name="Set as Background Image?")
    enable_dark_mode = models.BooleanField(default=False, verbose_name="Enable Dark Mode?")
    show_map_qrcode_on_invitation = models.BooleanField(default=True, verbose_name="Show Maps QR Code on Invitation?")
    
