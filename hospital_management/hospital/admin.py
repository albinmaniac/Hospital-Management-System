from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department, Doctor, Patient, Appointment

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization')
    search_fields = ('user__username', 'specialization')
    list_filter = ('department',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_number', 'address')
    search_fields = ('user__username',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date', 'time', 'status')
    search_fields = ('doctor__user__username', 'patient__user__username')
    list_filter = ('status', 'date')