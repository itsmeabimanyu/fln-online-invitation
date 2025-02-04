from django.db import models
from django.core.validators import EmailValidator
import uuid
from django.utils import timezone
from PIL import Image
from django.core.files.base import ContentFile
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

# Event Model - As before, representing an event to which people or companies are invited
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_name = models.TextField()
    from_event_date = models.DateTimeField()
    to_event_date = models.DateTimeField()
    # description = models.TextField()
    location = models.TextField()
    maps_location = models.TextField(blank=True, null=True)
    # event_type = models.CharField(max_length=50)  # e.g., "Wedding", "Conference"
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.event_name
    
    def soft_delete(self):
        self.deleted_at = timezone.now()  # Set waktu penghapusan
        self.save()

    def save(self, *args, **kwargs):
        if self.image:
            # Buka gambar yang diupload
            img = Image.open(self.image)
            # Cek ukuran gambar
            width, height = img.size
            # Resize hanya jika lebih besar dari 800x600, atau jika ingin menambahkan padding
            if width < 800 or height < 600:
                # Menambahkan padding agar gambar menjadi 800x600
                new_image = Image.new("RGB", (800, 600), (255, 255, 255))  # Padding putih
                new_image.paste(img, ((800 - width) // 2, (600 - height) // 2))  # Menempatkan gambar di tengah
                img = new_image  # Ganti gambar dengan padding
            else:
                # Resize menjadi 800x600 untuk gambar yang lebih besar
                img = img.resize((800, 600), Image.Resampling.LANCZOS)
            # Simpan gambar
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

    
