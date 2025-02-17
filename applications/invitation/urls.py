from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL for listing events
    # Chapter: Event
    path('', views.EventDashboardView.as_view(), name='event_dashboard'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/list/', views.EventListView.as_view(), name='event_list'),
    path('events/update/<uuid:pk>/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/delete/<uuid:pk>/', views.SoftDeleteEventView.as_view(), name='event_delete'),
    path('events/close/<uuid:pk>/', views.CloseEventView.as_view(), name='event_close'),

    # Chapter Participant
    path('participants/list/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/create/<uuid:pk>/', views.ParticipantCreateView.as_view(), name='participant_create'),
    path('participants/update/<uuid:pk>/', views.ParticipantUpdateView.as_view(), name='participant_update'),
    path('participants/delete/<uuid:pk>/', views.ParticipantDeleteView.as_view(), name='participant_delete'),
    path('participants/approve/<uuid:pk>/', views.ParticipantApproveView.as_view(), name='participant_approve'),
    path('participants/attendance/<uuid:pk>/', views.ParticipantAttendanceView.as_view(), name='participant_attendance'),
    path('participants/attendance/invitation/<uuid:pk>/', views.ParticipantAttendanceInviteView.as_view(), name='attendance_invitation'),

    # Chapter: Invitation
    path('invitation/create/<uuid:pk>/', views.InvitationStyleCreateView.as_view(), name='invitation_create'),
    path('invitation/update/<uuid:pk>/', views.InvitationStyleUpdateView.as_view(), name='invitation_update'),
    path('invitation/<uuid:pk>/', views.InvitationView.as_view(), name='invitation_detail'),
    path('invitation/success/<uuid:pk>/', views.ParticipantSuccessRegisterView.as_view(), name='success_register'),
    path('attendance/list/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/scan/', views.AttendanceScanView.as_view(), name='attendance_scan'),
    path('get-participant/', views.GetParticipant, name='get_participant'),
    
    # Chapter: Login/Logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # Register
    path('register/', views.RegisterView.as_view(), name='register'),

    # Short link
    path('<str:shortcode>/', views.redirect_shortlink, name='redirect_shortlink'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)