from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL for listing events
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/list/', views.EventListView.as_view(), name='event_list'),
    path('events/update/<uuid:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/delete/<uuid:pk>/', views.SoftDeleteEventView.as_view(), name='event_delete'),
    path('events/close/<uuid:pk>/', views.CloseEventView.as_view(), name='event_close'),
    path('participants/list/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/create/<uuid:pk>/', views.ParticipantCreateView.as_view(), name='participant_create'),
    path('participants/delete/<uuid:pk>/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
    path('invitation/<uuid:pk>/', views.InvitationView.as_view(), name='invitation_detail'),
    path('invitation/register/<uuid:pk>/', views.ParticipantRegisterCreateView.as_view(), name='participant_register'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)