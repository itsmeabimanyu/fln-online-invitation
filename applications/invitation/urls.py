from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL for listing events
    # path('events/', views.EventListView.as_view(), name='event_list'),
    path('', views.CompanyCreateView.as_view(), name='company_create'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/list/', views.EventListView.as_view(), name='event_list'),
    path('events/update/<uuid:pk>/', views.EventUpdateView.as_view(), name='event_update'),
     path('events/delete/<uuid:pk>/', views.SoftDeleteEvent.as_view(), name='event_delete'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)