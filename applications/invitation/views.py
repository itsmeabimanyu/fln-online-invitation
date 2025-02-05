from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, View, CreateView
from .models import Event, Participant
from .forms import EventForm, ParticipantForm
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

# Create your views here.
'''def crop_image(image, target_width, target_height):
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
    return ContentFile(output.read())'''

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/events_create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = " Create"
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
    template_name = 'pages/events_create.html'
    context_object_name = 'item'
    success_url = reverse_lazy('event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Event"
        items = self.model.objects.filter(deleted_at__isnull=True)
        context["items"] = items
        context["title_action"] = " Update"
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

class ParticipantListView(ListView):
    model = Participant
    template_name = 'pages/participants_list.html'
    context_object_name = 'items_list'

    """def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True).order_by('-is_active', 'from_event_date')"""

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
        context["items"] = self.model.objects.filter(invitation=self.event)
        context["event"] = self.event
        return context
    
    def form_valid(self, form):
        # Mendapatkan input data untuk guest_name dan guest_email yang bisa berupa list
        organizations = self.request.POST.getlist('organization')  # Menangani multiple guest_name
        guest_names = self.request.POST.getlist('guest_name')  # Menangani multiple guest_name
        guest_emails = self.request.POST.getlist('guest_email')  # Menangani multiple guest_email

        # Pastikan jumlah guest_name dan guest_email cocok
        if len(guest_names) == len(guest_emails):
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

        return redirect(self.request.META.get('HTTP_REFERER'))

class ParticipantDeleteView(View):
    def post(self, request, pk):
        item = get_object_or_404(Participant, pk=pk)
        item.delete() 
        return redirect(self.request.META.get('HTTP_REFERER'))
