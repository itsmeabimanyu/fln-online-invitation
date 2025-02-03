from django.db import models
from django.core.validators import EmailValidator
import uuid
from django.utils import timezone
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO

def crop_to_16_9(image):
    """
    Crop gambar ke rasio 16:9.
    :param image: File gambar yang diupload
    :return: Gambar yang sudah di-crop (PIL Image object)
    """
    img = Image.open(image)
    width, height = img.size
    target_ratio = 16 / 9
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Crop sisi kiri dan kanan
        new_width = int(height * target_ratio)
        left = (width - new_width) / 2
        top = 0
        right = (width + new_width) / 2
        bottom = height
    else:
        # Crop sisi atas dan bawah
        new_height = int(width / target_ratio)
        left = 0
        top = (height - new_height) / 2
        right = width
        bottom = (height + new_height) / 2

    # Crop gambar
    cropped_img = img.crop((left, top, right, bottom))

    # Konversi ke mode RGB jika gambar memiliki mode RGBA
    if cropped_img.mode == 'RGBA':
        cropped_img = cropped_img.convert('RGB')

    return cropped_img

# Event Model - As before, representing an event to which people or companies are invited
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.TextField()
    from_event_date = models.DateTimeField()
    to_event_date = models.DateTimeField()
    description = models.TextField()
    location = models.TextField()
    maps_location = models.TextField(blank=True, null=True)
    # event_type = models.CharField(max_length=50)  # e.g., "Wedding", "Conference"
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.event_name
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def save(self, *args, **kwargs):
        if self.image:
            # Crop gambar ke 16:9
            cropped_image = crop_to_16_9(self.image)
            # Simpan gambar yang sudah di-crop ke dalam BytesIO
            output = BytesIO()
            cropped_image.save(output, format='JPEG', quality=95)  # Simpan sebagai JPEG
            output.seek(0)
            # Simpan gambar ke field `image`
            self.image.save(
                self.image.name,
                ContentFile(output.read()),
                save=False
            )
        super().save(*args, **kwargs)

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

    
