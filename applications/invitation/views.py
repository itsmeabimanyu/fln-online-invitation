import os, base64, json, qrcode, ldap
from io import BytesIO
from PIL import Image

from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, View, CreateView, DetailView, TemplateView
from django.core.files.base import ContentFile
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.templatetags.static import static
from django.contrib.auth.views import LoginView
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.forms import modelformset_factory

from .models import Event, Participant, InvitationStyle
from .forms import EventForm, ParticipantForm, ParticipantRegisterForm, InvitationStyleForm, CustomLoginForm, RegisterForm

# Create your views here.
def redirect_shortlink(request, shortcode):
    shortlink = get_object_or_404(Event, short_link=shortcode, deleted_at__isnull=True, is_active=True)
    return redirect(reverse_lazy('invitation_detail', kwargs={'pk': shortlink.id}))

# Chapter: Event 
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/mainpages/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = "Create"
        context["subtitle"] = " Create View"
        context["text_submit"] = "Create"
        context["enable_preview_image"] = True
        return context
    
    def form_valid(self, form):
        form.instance.submitter = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

'''
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
'''
    
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'pages/mainpages/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True).order_by('-is_active', 'created_at', 'from_event_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Event'
        context['add_top_button'] = f"<button type='button' class='btn btn-info' onclick='window.location.href=\"{reverse('event_create')}\"'>Create Event</button>"
        context['title_action'] = 'List'
        context['text_submit'] = 'Create & View'
        context['subtitle'] = 'Events'
        context['fields'] = {
            'event_name': 'Event Name',
            'location': 'Location',
            'from_event_date': 'From Date',
            'to_event_date': 'To Date',
            'created_at': 'Created at',
            'submitter': 'User',
            'is_active': 'Is Active?'
        }

        # Content table action
        for item in context['items']:
            item.buttons_action = [
                f"<button type='button' class='btn btn-sm btn-info w-100 mb-1' onclick='window.location.href=\"{reverse('invitation_create', args=[item.id])}\"'>Invitation</button>"
                f"<button type='button' class='btn btn-sm btn-info w-100 mb-1' onclick='window.location.href=\"{reverse('participant_create', args=[item.id])}\"'>Participant</button>"
                f"<button type='button' class='btn btn-sm btn-warning w-100 mb-1' onclick='window.location.href=\"{reverse('event_update', args=[item.id])}\"'>Edit</button>"
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-first-{item.id}' class='btn btn-sm btn-{'secondary' if item.is_active else 'success'} w-100 mb-1'>{'Close' if item.is_active else 'Open'}</button>",
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-second-{item.id}' class='btn btn-sm btn-danger w-100 mb-1'>Delete</button>"
            ]

            # Content modal
            item.modals_form = {
                'Close Event' if item.is_active else 'Open Event': {
                    'modal_id': f'modal-first-{item.id}',
                    'action_url': reverse('event_close', kwargs={'pk': item.pk})
                },
                'Delete Event': {
                    'modal_id': f'modal-second-{item.id}',
                    'action_url': reverse('event_delete', kwargs={'pk': item.pk})
                }
            }

        return context
    
class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/mainpages/create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = " Update"
        context["subtitle"] = f"Update: {self.object.event_name}"
        context["text_submit"] = "Update"
        context["enable_preview_image"] = True
        context["active_status"] = '<div class="badge bg-success">Open</div>' if self.object.is_active else '<div class="badge bg-secondary">Close</div>'
        
        return context
    
    def form_valid(self, form):
        form.instance.submitter = self.request.user
        if 'image' in form.changed_data:  # Pastikan gambar diubah
            old_image_path = self.get_object().image.path
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)
   
class SoftDeleteEventView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Event, pk=pk)
        item.soft_delete() 
        # return redirect(self.request.META.get('HTTP_REFERER'))
        messages.success(self.request, 'Event deleted successfully!')
        return redirect('event_list')

class CloseEventView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Event, pk=pk)
        if item.is_active:
            item.close_event()  # Assuming this closes the event
            messages.success(request, 'Event closed successfully!')
        else:
            item.open_event()  # Assuming this opens the event
            messages.success(request, 'Event opened successfully!')
        return redirect('event_list')

# belum di pakai
class ParticipantListView(LoginRequiredMixin, ListView):
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
    
# Chapter: Participant
class ParticipantCreateView(LoginRequiredMixin, CreateView, ListView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'pages/mainpages/create_v2.html'
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'), is_active=True, deleted_at__isnull=True)
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(invitation=self.event)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "participant"
        context["title_action"] = " Create"
        context["subtitle"] = f"Participant: {self.event}"
        context["active_status"] = '<div class="badge bg-success">Open</div>' if self.event.is_active else '<div class="badge bg-secondary">Close</div>'

        # Content table action
        for item in context['items']:
            item.buttons_action = [
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-first-01-{item.id}' class='btn btn-sm btn-info w-100 mb-1'>Send Email</button>" if item.is_approved else
                f"<button type='button' class='btn btn-sm btn-warning w-100 mb-1' onclick='window.location.href=\"{reverse('participant_update', args=[item.id])}\"'>Edit</button>",
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-second-{item.id}' class='btn btn-sm btn-{'secondary' if item.is_approved else 'success'} w-100 mb-1'>{'Reject' if item.is_approved else 'Approve'}</button>",
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-third-{item.id}' class='btn btn-sm btn-danger w-100 mb-1'>Delete</button>", 
            ]

            # Content modal
            item.modals_form = {
                'Reject Participant' if item.is_approved else 'Approve Participant': {
                    'modal_id': f'modal-second-{item.id}',
                    'action_url': reverse('participant_approve', kwargs={'pk': item.pk})
                },
                'Delete Participant': {
                    'modal_id': f'modal-third-{item.id}',
                    'action_url': reverse('participant_delete', kwargs={'pk': item.pk})
                }
            }

        # Content table
        context["fields"] = {
            'is_approved': 'Approve?',
            'approved_by': 'Approved by'
        }

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

class ParticipantUpdateView(LoginRequiredMixin, UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = 'pages/mainpages/create.html'
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        # event yang aktif dan tidak statusnya dihapus
        self.participant = get_object_or_404(Participant, pk=self.kwargs.get('pk'), is_approved=False, invitation__deleted_at__isnull=True, invitation__is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Participant"
        # items = self.model.objects.filter(deleted_at__isnull=True)
        # context["items"] = items
        context["title_action"] = " Update"
        context["subtitle"] = f"Update: {self.object}"
        context["text_submit"] = "Update"
        context["active_status"] = '<div class="badge bg-success">Approved</div>' if self.object.is_approved else '<div class="badge bg-secondary">Pending to Approve</div>'
       
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Participant updated successfully!')
        return HttpResponseRedirect(reverse('participant_create', kwargs={'pk': self.participant.invitation.id}))

class ParticipantDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)
        item.delete() 
        return redirect(self.request.META.get('HTTP_REFERER'))
    
class ParticipantApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)

        if item.is_approved:
            item.is_approved = False
            item.approved_by = None
            item.save()
        else:
            item.approved_by = self.request.user
            item.approve_participant()      

        return redirect(self.request.META.get('HTTP_REFERER'))

class ParticipantAttendanceView(LoginRequiredMixin, View):
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
   
# Chapter: Invitation
class InvitationStyleCreateView(LoginRequiredMixin, CreateView):
    model = InvitationStyle
    form_class = InvitationStyleForm
    template_name = 'pages/mainpages/create.html'

    def dispatch(self, request, *args, **kwargs):
        # Get the event using the 'pk' from the URL kwargs
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'), is_active=True, deleted_at__isnull=True)

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
        context["subtitle"] = f'Create: {get_object_or_404(Event, id=self.event.id)}'
        context["text_submit"] = "Create & View"
        context["enable_preview_image"] = True
        context["active_status"] = '<div class="badge bg-success">Open</div>' if self.event.is_active else '<div class="badge bg-secondary">Close</div>'
        return context
    
    def form_valid(self, form):
        # Menyimpan event sebagai foreign key di model Invitation
        form.instance.event = self.event
        form.save()
        return HttpResponseRedirect(reverse('invitation_detail', kwargs={'pk': self.event.pk}))
    
class InvitationStyleUpdateView(LoginRequiredMixin, UpdateView):
    model = InvitationStyle
    form_class = InvitationStyleForm
    template_name = 'pages/mainpages/create.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        # Ambil object yang ingin diupdate
        item = self.get_object()

        # Periksa apakah 'deleted_at' pada relasi 'event' adalah null atau 'event' tidak aktif
        if item.event.deleted_at is not None or not item.event.is_active:
            # Jika deleted_at tidak null atau event tidak aktif, berarti objek ini sudah dihapus
            raise Http404("This invitation style's related event has been deleted or is inactive and cannot be updated.")

        # Jika passed, lanjutkan dengan proses UpdateView biasa
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "invitation"
        context["title_action"] = "update"
        context["subtitle"] = f'Update: {self.object.event.event_name}'
        context["text_submit"] = "Update & View"
        context["enable_preview_image"] = True
        context["active_status"] = '<div class="badge bg-success">Open</div>' if self.object.event.is_active else '<div class="badge bg-secondary">Close</div>'
        context["additional_button"] = f"<button type='button' class='btn btn-primary' onclick='window.location.href=\"{reverse('invitation_detail', args=[self.object.event.id])}\"'>View</button>"
        return context

    def form_valid(self, form):
        invitation_style = form.save(commit=False)
        invitation_style.save()
        return HttpResponseRedirect(reverse('invitation_detail', kwargs={'pk': self.object.event.id}))

# Chapter: Invitation additional
class InvitationView(CreateView):
    model = Participant
    form_class = ParticipantRegisterForm
    # fields = ["organization", "guest_name"]
    template_name = 'pages/additionals/invitation_view.html'
    context_object_name = 'item'

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=self.kwargs.get('pk'), deleted_at__isnull=True, is_active=True)
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
    template_name = 'pages/additionals/success_register.html'

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
class AttendanceListView(LoginRequiredMixin, ListView):
    model = Participant
    template_name = 'pages/mainpages/list.html'
    context_object_name = 'items'
    ordering = ['-attendance_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_approved=True, invitation__is_active=True)

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

        # Content table action
        for item in context['items']:
            item.buttons_action = [
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-first-{item.id}' class='btn btn-sm btn-{'secondary' if item.is_attending else 'success'} w-100 mb-1'>{'Not Attend' if item.is_attending else 'Attend'}</button>",
                f"<button type='button' data-bs-toggle='modal' data-bs-target='#modal-second-{item.id}' class='btn btn-sm btn-info w-100'>Detail</button>"
            ]

            # Content modal
            item.modals_form = {
                'Mark as Absent' if item.is_attending else 'Mark as Present': {
                    'modal_id': f'modal-first-{item.id}',
                    'action_url': reverse('participant_attendance', kwargs={'pk': item.pk})
                }
            }
            item.modals_detail = {
                'Details Participant': {
                    'modal_id': f'modal-second-{item.id}',
                },
            }

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
 
# Chapter: Attendance additional
class AttendanceScanView(LoginRequiredMixin, ListView):
    model = Participant
    template_name = 'pages/additionals/attendance_scan.html'
    context_object_name = 'items'
    ordering = ['-attendance_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_approved=True, is_attending=True, invitation__is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Attendance'
        context['title_action'] = 'Check-In'
        context['subtitle'] = 'Scan QR Participant'
        context['fields'] = {
            'organization': 'Organization',
            'guest_name': 'Guest Name',
            'invitation': 'Event Invitation',
            'attendance_time': 'Attendance Time',
        }
        return context

# Get response from Attendance additional
@csrf_exempt
def GetParticipant(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request
            data = json.loads(request.body)
            # Extract the 'scanned_data' which is assumed to be the Participant ID
            scanned_data = data.get('scanned_data')
            # Get the Participant object based on the scanned_data (assumed to be the ID)
            guest = get_object_or_404(Participant, id=scanned_data, is_approved=True, invitation__is_active=True)
            # Render the partial template with the participant data
            return render(request, 'pages/partials/partial_scan.html', {'item': guest})
        except Exception as e:
            # Handle any errors
            return render(request, 'pages/partials/partial_scan.html', {'error': str(e)})
    # If not a POST request, return some default response or a 404.
    return render(request, 'pages/partials/partial_scan.html', {'error': 'Invalid request method'})

# Chapter: Dasboard
class EventDashboardView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'pages/dashboards/events.html'
    context_object_name = 'items'
    ordering = ['-is_active', 'from_event_date']
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Events'
        context['title_action'] = 'Dashboard'
        context['add_top_button'] = f"<button type='button' class='btn btn-info' onclick='window.location.href=\"{reverse('event_create')}\"'>Create Event</button>"
        context['fields'] = {
            'from_event_date': '<p class="card-text"><i class="align-middle me-2" data-feather="calendar"></i>From Date Time</p>',
            'to_event_date': '<p class="card-text"><i class="align-middle me-2" data-feather="calendar"></i>To Date Time</p>',
            'location': '<p class="card-text"><i class="align-middle me-2" data-feather="map-pin"></i>Location</p>',
        }
        for item in context['items']:
            item.card_image = item.image.url if item.image else static('images/default_1280_720.jpg')
            item.card_text_status = '' if item.is_active else '<p class="fs-2 text-overlay text-light">CLOSED</p>'
            item.card_title = item.event_name
            item.card_subtitle = item.description
            item.card_badge = '<span class="badge bg-success">Open</span>' if item.is_active else '<span class="badge bg-secondary">Close</span>'
            item.additional_url = f"<button type='button' class='dropdown-item' onclick='window.location.href=\"{reverse('invitation_create', args=[item.id])}\"'>Invitation</button>"
            item.additional_url_01 = f"<button type='button' class='dropdown-item' onclick='window.location.href=\"{reverse('participant_create', args=[item.id])}\"'>Participant</button>"

        return context

# Chapter: Login
class LoginView(LoginView):
    template_name = 'layouts/base_login.html'
    success_url = reverse_lazy('event_dashboard')
    form_class = CustomLoginForm 

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.is_active:
            return redirect(self.success_url)  # Redirect to the home page if already authenticated
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign in'
        context['title_action'] = 'Sign in to your account to continue'
        context['subtitle'] = 'Event Invitation'
        context["text_submit"] = "Login"
        return context

    def form_valid(self, form):
        # Cek login biasa (menggunakan database lokal)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            # Jika login biasa gagal, coba autentikasi menggunakan LDAP
            ldap_user = self.authenticate_ldap(username, password)
            if ldap_user:
                # Jika login LDAP sukses, buat/mendapatkan user dari LDAP
                user = self.create_or_get_user_from_ldap(username)
                login(self.request, user)
                return super().form_valid(form)
            else:
                form.add_error(None, 'Invalid credentials.')
                return self.form_invalid(form)

    def authenticate_ldap(self, username, password):
        try:
            ldap_connection = ldap.initialize(settings.LDAP_SERVER)
            ldap_connection.simple_bind_s(f"uid={username},ou=users,dc=example,dc=com", password)
            return True  # Jika bind berhasil, dianggap login sukses
        except ldap.LDAPError:
            return False  # Jika gagal, return False
    
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # logout(request)
        request.session.flush()
        return redirect(settings.LOGOUT_REDIRECT_URL)

# Chapter Register for development
class RegisterView(CreateView):
    form_class = RegisterForm  # Form yang digunakan
    template_name = 'layouts/base_login.html'  # Template untuk form registrasi
    success_url = reverse_lazy('event_dashboard')  # URL tujuan setelah registrasi berhasil

    def form_valid(self, form):
        # Simpan user
        user = form.save()

        # Tentukan backend autentikasi secara manual
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        # Login pengguna
        login(self.request, user)

        # Redirect ke halaman sukses
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign up'
        context['title_action'] = 'Sign up to your account to continue'
        context['subtitle'] = 'Event Invitation'
        context["text_submit"] = "Register"
        return context