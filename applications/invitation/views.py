from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, View, CreateView, DetailView, TemplateView
from .models import Event, Participant, InvitationStyle
from .forms import EventForm, ParticipantForm, ParticipantRegisterForm, InvitationStyleForm
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
import qrcode
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.views import APIView
from django.utils import timezone

# Create your views here.
'''
def crop_image(image, target_width, target_height):
    img = Image.open(image)
    width, height = img.size
    target_ratio = 16 / 9
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        top = 0
        right = left + new_width
        bottom = height
    else:
        new_height = int(width / target_ratio)
        left = 0
        top = (height - new_height) // 2
        right = width
        bottom = top + new_height

    img = img.crop((left, top, right, bottom))
    img = img.resize((target_width, target_height), Image.ANTIALIAS)

    output = BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)
    return ContentFile(output.read())
'''

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/invitation/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = " Create"
        context["subtitle"] = " Create New"
        context["text_submit"] = "Create"
        return context
    
class EventListView(ListView):
    model = Event
    template_name = 'pages/events_list.html'
    context_object_name = 'items_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True).order_by('-is_active', 'from_event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Events"
        context["form"] = EventForm()
        for item in context['items_list']:
            item.update_url = reverse('event_update', kwargs={'pk': item.id})
            item.delete_url = reverse('event_delete', kwargs={'pk': item.id})
            item.close_url = reverse('event_close', kwargs={'pk': item.id})
            item.form = EventForm(instance=item)
        return context
    
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/invitation/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = " Update"
        context["subtitle"] = f"Update {self.object.event_name}"
        context["text_submit"] = "Update"
        context["active_status"] = self.object.is_active
        return context
    
    def form_valid(self, form):
        obj = self.get_object()  # Ambil objek lama
        if 'image' in form.changed_data:  # Cek apakah gambar diubah
            if obj.image: 
                old_image_path = obj.image.path  
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)  # Hapus gambar lama
        return super().form_valid(form)
    
class SoftDeleteEventView(View):
    def post(self, request, pk):
        item = get_object_or_404(Event, pk=pk)
        item.soft_delete() 
        # return redirect(self.request.META.get('HTTP_REFERER'))
        return redirect('event_list')

class CloseEventView(View):
    def post(self, request, pk):
        item = get_object_or_404(Event, pk=pk)
        if item.is_active:
            item.close_event()
        else:
            item.open_event()
        # return redirect(self.request.META.get('HTTP_REFERER'))
        return redirect('event_list')

# belum di pakai
class ParticipantListView(ListView):
    model = Participant
    template_name = 'pages/participants_list.html'
    context_object_name = 'items_list'

    """
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True).order_by('-is_active', 'from_event_date')
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Event.objects.filter(is_active=True, deleted_at__isnull=True)
        context["items"] = items
        context["title"] = "Events"

        return context
    
"""
class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'pages/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Participant"
        context["title_action"] = " Create"
        return context
"""

class ParticipantCreateView(CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'pages/create.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "participant"
        context["title_action"] = " Create"
        context["active_status"] = self.event.is_active
        context["event"] = self.event
        object_item = self.model.objects.filter(invitation=self.event)
        for item in object_item:
            item.delete_url = reverse('participant_delete', kwargs={'pk': item.pk})
            item.approve_url = reverse('participant_approve', kwargs={'pk': item.pk})
            item.attendance_url = reverse('participant_attendance', kwargs={'pk': item.pk})
            item.action = "reject" if item.is_approved else "approve"
            item.action_attendance = "mark not attending" if item.is_attending else "mark attending"
            item.action_color = "info" if item.is_approved else "secondary"
        context["items"] = object_item
        return context
    
    def form_valid(self, form):
        # Mendapatkan input data untuk guest_name dan guest_email yang bisa berupa list
        organizations = self.request.POST.getlist('organization')  # Menangani multiple guest_name
        guest_names = self.request.POST.getlist('guest_name')  # Menangani multiple guest_name
        emails = self.request.POST.getlist('email')  # Menangani multiple guest_email

        # Pastikan jumlah guest_name dan guest_email cocok
        '''
        if len(guest_names):
            for name, email, organization in zip(guest_names, guest_emails, organizations):
                # Membuat Participant baru untuk setiap pasangan name dan email
                Participant.objects.create(
                    # organization=form.cleaned_data['organization'],
                    invitation=self.event,
                    organization=organization,
                    guest_name=name,
                    guest_email=email
                )
        else:
            # Jika jumlah guest_name dan guest_email tidak cocok
            form.add_error('guest_name', 'Jumlah guest_name dan guest_email tidak cocok.')

            # Mengembalikan response jika ada error
            return self.form_invalid(form)
        '''
        for name, email, organization in zip(guest_names, emails, organizations):
            # Membuat Participant baru untuk setiap pasangan name dan email
            Participant.objects.create(
                # organization=form.cleaned_data['organization'],
                invitation=self.event,
                organization=organization,
                guest_name=name,
                email=email
            )

        return redirect(self.request.META.get('HTTP_REFERER'))

class ParticipantDeleteView(View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)
        item.delete() 
        return redirect(self.request.META.get('HTTP_REFERER'))
    
class ParticipantApproveView(View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)

        if item.is_approved:
            item.is_approved = False
            item.save()
        else:
            item.approve_participant()      

        return redirect(self.request.META.get('HTTP_REFERER'))

# Chapter: Invitation
class InvitationStyleCreateView(CreateView):
    model = InvitationStyle
    form_class = InvitationStyleForm
    template_name = 'pages/invitation/create.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the event using the 'pk' from the URL kwargs
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))

        # Check if the InvitationStyle already exists for the event
        try:
            invitation_style = InvitationStyle.objects.get(event=self.event)
            # If it exists, redirect to the update page
            return HttpResponseRedirect(reverse('invitation_update', kwargs={'pk': invitation_style.id}))
        except InvitationStyle.DoesNotExist:
            # If it does not exist, proceed to the creation view
            pass

        # If no redirection occurs, proceed with the normal dispatch
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "invitation"
        context["title_action"] = "create"
        context["subtitle"] = get_object_or_404(Event, id=self.event.id)
        context["text_submit"] = "Create & View"
        context["active_status"] = self.event.is_active
        return context
    
    def form_valid(self, form):
        # Menyimpan event sebagai foreign key di model Invitation
        form.instance.event = self.event
        form.save()
        return HttpResponseRedirect(reverse('invitation_detail', kwargs={'pk': self.event.pk}))
    
class InvitationStyleUpdateView(UpdateView):
    model = InvitationStyle
    form_class = InvitationStyleForm
    template_name = 'pages/invitation/create.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "invitation"
        context["title_action"] = "update"
        context["subtitle"] = self.object.event.event_name
        context["text_submit"] = "Update & View"
        context["active_status"] = self.object.event.is_active
        context["additional_button"] = f"<button type='button' class='btn btn-primary' onclick='window.location.href=\"{reverse('invitation_detail', args=[self.object.event.id])}\"'>View</button>"
        return context

    def form_valid(self, form):
        invitation_style = form.save(commit=False)
        invitation_style.save()
        return HttpResponseRedirect(reverse('invitation_detail', kwargs={'pk': self.object.event.id}))

class InvitationView(CreateView):
    model = Participant
    form_class = ParticipantRegisterForm
    # fields = ["organization", "guest_name"]
    template_name = 'pages/invitation/view.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Mendapatkan input data untuk guest_name dan guest_email yang bisa berupa list
        organization = self.request.POST.get('organization')  # Jika organization adalah single value
        email = self.request.POST.get('email') 
        guest_names = self.request.POST.getlist('guest_name')  # Menangani multiple guest_name
        # guest_emails = self.request.POST.getlist('guest_email')  # Menangani multiple guest_email

        # Validasi: Pastikan jumlah guest_names dan guest_emails sama
        """
        if len(guest_names) != len(guest_emails):
            raise ValueError("Jumlah guest_name dan guest_email tidak sama.")
        """

        # Iterasi untuk membuat Participant baru
        # for name, email in zip(guest_names, guest_emails):
        for name in guest_names:  # Tidak perlu menggunakan zip jika hanya satu iterable
            Participant.objects.create(
                invitation=self.event,  # Pastikan self.event sudah terdefinisi
                email=email,
                organization=organization,
                guest_name=name,
                # guest_email=email
            )

        # messages.success(self.request, 'Thank you for your response! You will now wait for a response from us.')
        return redirect(reverse_lazy('success_register', kwargs={'pk': self.event.id}))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["description_title_form"] = "Please kindly fill out the form below."
        item = get_object_or_404(InvitationStyle, event=self.event)
        item.background = "background-color: #2e313d;" if item.enable_dark_mode else "background-color: #e8e7ea;"
        item.card_color = "background-color: #353744; color: #bdc4c9" if item.enable_dark_mode else "background-color: #fff;"
        context["item"] = item
        if self.event.maps_location:
            # Membuat QR Code berdasarkan maps_location (misalnya URL)
            qr = qrcode.QRCode(
                version=1,  # Ukuran QR code
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Level koreksi kesalahan
                box_size=10,  # Ukuran box pada QR code
                border=4,  # Ketebalan border
            )
            qr.add_data(self.event.maps_location)  # Menambahkan data ke QR code
            qr.make(fit=True)

            # Membuat gambar QR code dengan foreground hitam dan background putih
            img = qr.make_image(fill='black', back_color='white')
            if item.enable_dark_mode:
                img = qr.make_image(fill_color='papayawhip', back_color='white')

            # Mengonversi gambar menjadi format PNG dengan background transparan
            img = img.convert("RGBA")  # Convert to RGBA (supports transparency)
            datas = img.getdata()

            # Membuat background transparan
            new_data = []
            for item in datas:
                # Mengubah warna putih menjadi transparan
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    new_data.append((255, 255, 255, 0))  # Transparan
                else:
                    new_data.append(item)
            img.putdata(new_data)

            # Menyimpan gambar ke dalam buffer BytesIO (in-memory image)
            qr_image = BytesIO()
            img.save(qr_image, "PNG")
            qr_image.seek(0)

            # Mengonversi gambar menjadi base64
            qr_image_base64 = base64.b64encode(qr_image.getvalue()).decode('utf-8')

            # Menambahkan string base64 ke dalam context
            context['qr_image'] = qr_image_base64

        return context
    
class ParticipantSuccessRegisterView(TemplateView):
    template_name = 'pages/invitation/success_register.html'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["description_title_form"] = "Please kindly fill out the form below."
        item = get_object_or_404(InvitationStyle, event=self.event)
        item.background = "background-color: #2e313d;" if item.enable_dark_mode else "background-color: #e8e7ea;"
        item.card_color = "background-color: #353744; color: #bdc4c9" if item.enable_dark_mode else "background-color: #fff;"
        context["item"] = item
        return context
    
# Chapter: Attendance
class AttendanceListView(ListView):
    model = Participant
    template_name = 'pages/invitation/list.html'
    context_object_name = 'items'
    ordering = ['-attendance_time']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Attendance'
        context['add_top_button'] = f"<button type='button' class='btn btn-info' onclick='window.location.href=\"{reverse('attendance_scan')}\"'>Scan Attendance</button>"
        context['title_action'] = 'List'
        context['text_submit'] = 'Create & View'
        context['subtitle'] = 'Participant'
        context['fields'] = {
            'organization': 'Organization',
            'guest_name': 'Guest Name',
            'invitation': 'Event Invitation',
            'attendance_time': 'Attendance Time',
            'is_attending': 'Attendance?',
        }

        for item in context['items']:
            item.li_first = 'Mark not attending ' if item.is_attending else 'Mark attending'
            item.text_modal_first = 'attendance'
            item.url_li_first = reverse('participant_attendance', kwargs={'pk': item.pk})
            item.li_second = 'Details'
            item.text_modal_second = 'details'

            # Create a QR code
            qr = qrcode.make(item.id)
            # Save the QR code to a BytesIO object
            img = BytesIO()
            qr.save(img, 'PNG')
            img.seek(0)
            # Convert image to base64 string
            qr_image_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
            # Add the base64 string to the item as qr_image
            item.qr_image = f"data:image/png;base64,{qr_image_base64}"

        return context

class AttendanceScanView(TemplateView):
    template_name = 'pages/scan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Attendance'
        context['title_action'] = 'Check-In'
        context['subtitle'] = 'Scan QR Participant'
        return context

class ParticipantAttendanceView(View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)
        if item.is_attending:
            item.is_attending = False
            item.attendance_time = None
            item.save()
            messages.success(request, 'Attendance marked as absent successfully.')  # Success message
        else:
            item.mark_attendance()
            messages.success(request, 'Attendance marked successfully.')  # Success message
        return redirect(self.request.META.get('HTTP_REFERER'))

@csrf_exempt
def GetParticipant(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request
            data = json.loads(request.body)
            # Extract the 'scanned_data' which is assumed to be the Participant ID
            scanned_data = data.get('scanned_data')
            # Get the Participant object based on the scanned_data (assumed to be the ID)
            guest = get_object_or_404(Participant, id=scanned_data, is_approved=True)
            # Render the partial template with the participant data
            return render(request, 'pages/partials/partial_scan.html', {'item': guest})
        except Exception as e:
            # Handle any errors
            return render(request, 'pages/partials/partial_scan.html', {'error': str(e)})
    # If not a POST request, return some default response or a 404.
    return render(request, 'pages/partials/partial_scan.html', {'error': 'Invalid request method'})