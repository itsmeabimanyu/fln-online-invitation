from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, CreateView
from .models import Event, Organization
from .forms import EventForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
# Event List View: List all events
class EventListView(ListView):
    model = Event
    template_name = 'pages/list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Events List"
        return context
    

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/create.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Events Create"
        return context

class CompanyCreateView(CreateView):
    model = Organization
    fields = ["name", "address", "email"]
    template_name = 'dashboard.html'
    context_object_name = 'events'