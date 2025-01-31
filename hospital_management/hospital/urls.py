from django.urls import path
from .views import (
    DoctorRegistrationView,DoctorListView,DoctorDetailView,DoctorUpdateView,DoctorDeleteView,
    PatientRegistrationView,PatientListView,PatientDetailView,PatientUpdateView,PatientDeleteView,
    AppointmentCreateView,AppointmentListView,AppointmentDetailView,AppointmentUpdateView,AppointmentDeleteView,AppointmentStatusUpdateView,
    DashboardView,DoctorAppointmentListView,PatientAppointmentListView

    )

urlpatterns = [

    path('register/doctor/', DoctorRegistrationView.as_view(), name='doctor_register'),
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/<int:pk>/update/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctors/<int:pk>/delete/', DoctorDeleteView.as_view(), name='doctor_delete'),

    path('register/patient/', PatientRegistrationView.as_view(), name='patient_register'),
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/update/', PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),

    path('appointments/book/', AppointmentCreateView.as_view(), name='appointment_book'),
    path('appointments/', AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/update/<int:pk>/', AppointmentUpdateView.as_view(), name='appointment_update'),
    path('appointments/cancel/<int:pk>/', AppointmentDeleteView.as_view(), name='appointment_cancel'),
    path('appointments/status/<int:pk>/', AppointmentStatusUpdateView.as_view(), name='appointment_status_update'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('doctor/appointments/', DoctorAppointmentListView.as_view(), name='doctor_appointment_list'),
    path('patient/appointments/', PatientAppointmentListView.as_view(), name='patient_appointment_list'),
]
  

