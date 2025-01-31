from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction  # To ensure atomicity
from django.contrib.auth import get_user_model
from hospital.models import Doctor, Department,Patient,Appointment
from django.utils.timezone import now

User = get_user_model()
class DoctorRegistrationForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    specialization = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','gender', 'email', 'password1', 'password2']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        with transaction.atomic():  # Ensure atomicity
            # Save the user instance
            user = super().save(commit=False)
            user.role = 'doctor'
            if commit:
                user.save()
                # Create a Doctor instance associated with this user
                Doctor.objects.create(
                    user=user,
                    department=self.cleaned_data['department'],
                    specialization=self.cleaned_data['specialization'],
                )
        return user


User = get_user_model()  # Get the custom User model

class PatientRegistrationForm(UserCreationForm):
    contact_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','gender', 'email', 'password1', 'password2']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }


    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'  # Assign the 'patient' role
        if commit:
            user.save()  # Save the User instance
            # Create the associated Patient instance
            Patient.objects.create(
                user=user,
                contact_number=self.cleaned_data['contact_number'],
                address=self.cleaned_data['address'],
                date_of_birth=self.cleaned_data['date_of_birth']
            )
        return user
    

class AppointmentBookingForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        required=True,
        label="Select Doctor",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="Appointment Date",
        required=True
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control'
        }),
        label="Appointment Time",
        required=True
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Reason for Appointment'
        }),
        label="Reason for Appointment",
        required=True,
        max_length=500
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']


class AppointmentUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'status', 'reason']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Explicitly pass the user
        super().__init__(*args, **kwargs)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < now().date():
            raise forms.ValidationError("The appointment date cannot be in the past.")
        return date

    def clean_status(self):
        status = self.cleaned_data['status']
        if status == 'approved' and self.user.role not in ['doctor', 'admin']:
            raise forms.ValidationError("Only doctors or admins can approve appointments.")
        return status