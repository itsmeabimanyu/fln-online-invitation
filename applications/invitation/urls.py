from django.urls import path
from . import views

urlpatterns = [
    # URL for listing events
    # path('events/', views.EventListView.as_view(), name='event_list'),
    path('company/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('events/create/', views.EventCreateView.as_view(), name='create_event'),
    path('events/list/', views.EventListView.as_view(), name='list_event'),
]