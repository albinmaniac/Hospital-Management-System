from django.db import models
from accounts.models import User


# Create your models here.



class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    specialization = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male') 

    @property
    def full_name(self):
        # Construct full name or provide fallback if unavailable
        return f"{self.user.first_name or ''} {self.user.last_name or ''}".strip() or "Unknown Doctor"

    def __str__(self):
        # Return the full name when the object is represented as a string
        return self.full_name
    


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,null=True,blank=True) 

    def __str__(self):
        return self.user.get_full_name()
    


from django.core.exceptions import ValidationError
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField()

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.last_name} on {self.date} at {self.time}"
    
    def approve(self, user):
     if user.role in ['doctor', 'admin']:
        self.status = 'approved'
        self.save()
     else:
        raise ValidationError("Only doctors or admins can approve appointments.")
        
    def can_patient_edit(self):
        return self.status == 'pending'
    
    def save(self, *args, **kwargs):
        if self.pk and self.status == 'approved':
            self.status = 'pending'
        super().save(*args, **kwargs)