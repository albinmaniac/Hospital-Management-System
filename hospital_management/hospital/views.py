from django.shortcuts import render,redirect,get_object_or_404
from .models import Doctor,Patient,Department,Appointment
from django.views.generic import FormView,ListView,DetailView,DeleteView,UpdateView,TemplateView
from .forms import DoctorRegistrationForm,PatientRegistrationForm,AppointmentBookingForm
from django.urls import reverse_lazy
from django.contrib.auth import login,logout
from django.views.generic.edit import UpdateView,DeleteView,CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from accounts.models import User  # Assuming your custom User model is in accounts.models
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


#===========Doctor =============

class DoctorRegistrationView(FormView):
    template_name = 'doctor_register.html'
    form_class = DoctorRegistrationForm
    success_url = '/hospital/dashboard/'  # Replace with your success URL , /hospital/dashboard/

    def form_valid(self, form):
        form.save()  # Save the doctor and user instance
        return super().form_valid(form)


class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctor_list.html'  # Custom template
    context_object_name = 'doctors'

    def dispatch(self, request, *args, **kwargs):
        # Allow only patients, doctors, or admins to access this page
        allowed_roles = ['patient', 'doctor', 'admin']
        if request.user.role not in allowed_roles:
            return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Customize the query if needed (currently fetching all doctors)
        return Doctor.objects.all()


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctor_detail.html'  # Custom template
    context_object_name = 'doctor'

    

class DoctorUpdateView(UpdateView):
    model = Doctor
    fields = ['department', 'specialization']  # Fields that can be updated
    template_name = 'doctor_update.html'
    success_url = '/hospital/doctors/'  # Redirect to the doctors list after update

    def dispatch(self, request, *args, **kwargs):
        # Restrict access to admins only
        if request.user.role != 'admin':
            return HttpResponseForbidden("You do not have permission to update doctor details.Go backkk!!!!")
        return super().dispatch(request, *args, **kwargs)
    

class DoctorDeleteView(DeleteView):
    model = Doctor
    template_name = 'doctor_confirm_delete.html'
    success_url = reverse_lazy('doctor_list')  


#=======Patient =========


class PatientRegistrationView(FormView):
    template_name = 'patient_register.html'
    form_class = PatientRegistrationForm
    success_url = reverse_lazy('dashboard')  # Redirect to the dashboard after registration

    def form_valid(self, form):
        # Save the user and log them in
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = 'Patient'
        return context


class PatientListView(ListView):
    model = Patient
    template_name = 'patient_list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        # Customize query if needed (e.g., filter by criteria)
        return Patient.objects.select_related('user').all()
    
    def dispatch(self, request, *args, **kwargs):
        # Allow only patients, doctors, or admins to access this page
        if request.user.role not in ['patient', 'doctor', 'admin']:
            return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)


class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patient_detail.html'
    context_object_name = 'patient'

    def get_queryset(self):
        # Ensure patient details can be accessed
        return Patient.objects.select_related('user')
    


class PatientUpdateView(UpdateView):
    model = Patient
    template_name = 'patient_update.html'
    fields = ['date_of_birth', 'contact_number', 'address','gender']
    success_url = '/hospital/patients/'  # Redirect to the patient list after updating

    def get_queryset(self):
        # Ensure that only the patient themselves or admins can update the profile
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
class PatientDeleteView(DeleteView):
    model = Patient
    template_name = 'patient_confirm_delete.html'
    success_url = '/patients/'  # Redirect to patient list after deletion

    def get_queryset(self):
        # Restrict deletion to authorized users (e.g., admins)
        return Patient.objects.all()
    


#===========Appointment =============

class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentBookingForm
    template_name = 'appointment_booking.html'
    success_url = reverse_lazy('appointment_list')

    def form_valid(self, form):
    # Get the Patient instance associated with the logged-in user
        try:
            patient = Patient.objects.get(user=self.request.user)
            form.instance.patient = patient  # Assign the Patient instance
        except Patient.DoesNotExist:
            # Handle the case where the logged-in user is not a Patient
            form.add_error(None, "You must be registered as a Patient to book an appointment.")
            return self.form_invalid(form)

        return super().form_valid(form)


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    context_object_name = 'appointments'
    template_name = 'appointment_list.html'  # Default for patients

    def get_queryset(self):
        user = self.request.user

        if user.role == 'patient':
            # Get the Patient instance for the logged-in user
            patient = get_object_or_404(Patient, user=user)
            return Appointment.objects.filter(patient=patient)

        elif user.role == 'doctor':
            # Get the Doctor instance for the logged-in user
            doctor = get_object_or_404(Doctor, user=user)
            # Fetch appointments with related patient details
            return Appointment.objects.select_related('patient', 'patient__user').filter(doctor=doctor)

        elif user.role == 'admin':
            # Admins see all appointments with related patient and doctor details
            return Appointment.objects.select_related('patient', 'doctor', 'patient__user', 'doctor__user').all()

        raise PermissionDenied("You are not authorized to view this page.")
        

    def get_template_names(self):
        # Use templates based on the user's role
        if self.request.user.role == 'doctor':
            return ['doctor_appointment_list.html']
        elif self.request.user.role == 'admin':
            return ['admin_appointment_list.html']
        return [self.template_name]  # Default to patient template


class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'appointment_detail.html'
    context_object_name = 'appointment'

    def get_object(self):
        # Ensure the appointment is for the logged-in doctor
        return get_object_or_404(
            Appointment,
            id=self.kwargs['pk'],
            doctor__user=self.request.user,
        )
    

class AppointmentUpdateView(UpdateView):
    model = Appointment
    fields = ['date', 'time', 'reason']
    template_name = 'appointment_update.html'
    success_url = reverse_lazy('appointment_list')

    def get_object(self, queryset=None):
        # Ensure only the patient's own appointments can be updated
        appointment = get_object_or_404(Appointment, id=self.kwargs['pk'], patient=self.request.user)
        return appointment
    

class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = 'appointment_cancel.html'
    success_url = reverse_lazy('appointment_list')

    def get_object(self, queryset=None):
        # Ensure only the patient's own appointments can be deleted
        appointment = get_object_or_404(Appointment, id=self.kwargs['pk'], patient=self.request.user)
        return appointment
    
# 
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.views import View
from .models import Appointment

class AppointmentStatusUpdateView(View):
    def post(self, request, pk):
        # Ensure only doctors and admins can update
        if request.user.role not in ['doctor', 'admin']:
            return HttpResponseForbidden("You do not have permission to update appointment status.")

        # Get the appointment
        appointment = get_object_or_404(Appointment, id=pk)

        # Ensure only the assigned doctor can approve/cancel it
        if request.user.role == 'doctor' and appointment.doctor.user != request.user:
            return HttpResponseForbidden("You can only modify your own appointments.")

        # Update the status based on the submitted value
        status = request.POST.get('status')  # Get 'approved' or 'canceled' from the form
        if status in ['approved', 'canceled']:
            appointment.status = status
            appointment.save()

        # Redirect based on the role
        if request.user.role == 'admin':
            return redirect('admin_appointment_list')  # Change this to the actual admin appointment list URL
        else:
            return redirect('doctor_appointment_list')  # Redirect doctors to their own list
#Dashboard

#===============Dashboard==============

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the current user
        user = self.request.user

        # Determine the role and provide data accordingly
        if user.role == 'patient':
            # Patient-specific data
            try:
                patient = Patient.objects.get(user=user)  # Get the Patient instance
                context['appointments'] = Appointment.objects.filter(patient=patient)
            except Patient.DoesNotExist:
                context['appointments'] = []  # No appointments if the Patient instance doesn't exist

        elif user.role == 'doctor':
            # Doctor-specific data
            try:
                doctor = Doctor.objects.get(user=user)  # Get the Doctor instance
                context['appointments'] = Appointment.objects.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                context['appointments'] = []  # No appointments if the Doctor instance doesn't exist

        elif user.role == 'admin':
            # Admin-specific data
            context['doctors'] = Doctor.objects.all()
            context['patients'] = Patient.objects.all()
            context['appointments'] = Appointment.objects.all()

        else:
            context['message'] = "Role not recognized."

        return context
    

#==========Seprate Appointment List View ==================

class DoctorAppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'doctor_appointment_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        # Get the logged-in doctor
        doctor = get_object_or_404(Doctor, user=self.request.user)

        # Use select_related to include patient and user data for efficiency
        return Appointment.objects.select_related('patient__user').filter(doctor=doctor).order_by('date', 'time')
#

class PatientAppointmentListView(ListView):
    model = Appointment
    template_name = 'patient_appointment_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        # Show only appointments where the logged-in user is the patient
        return Appointment.objects.filter(patient=self.request.user)


