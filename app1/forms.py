from django import forms
from .models import CustomUser
from datetime import date
from .models import blood_choice
from django.core.validators import RegexValidator


# Define blood group choices

class DonorForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1900, date.today().year - 18 + 1)),
        required=True
    )
    has_disease = forms.BooleanField(required=False)
    bloodgroup = forms.ChoiceField(choices=blood_choice, required=True)
    weight = forms.IntegerField(min_value=40, required=True)  # Assuming weight is in kilograms
    last_donation_date = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, date.today().year + 1)), required=False)

    password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'contact')

class ReceiverForm(forms.ModelForm):
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, date.today().year + 1)), required=True)
    bloodgroup_needed = forms.ChoiceField(choices=blood_choice, required=True)
    quantity_required = forms.IntegerField(min_value=1, required=True)
    request_status = forms.ChoiceField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], initial='Pending')
    password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'contact')


class BloodBankForm(forms.ModelForm):
    blood_centre_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': 'Blood Bank Centre\'s Name'}))
    license_number = forms.CharField(max_length=15, required=True, validators=[RegexValidator(regex=r'^[A-Za-z0-9]{15}$', message="License number must be 15 alphanumeric characters.")], widget=forms.TextInput(attrs={'placeholder': 'License Number'}))
    blood_inventory = forms.JSONField(required=True, widget=forms.Textarea(attrs={'placeholder': 'Blood Inventory in this format (e.g., {"A+": 100, "B+": 200})'}))
    password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, max_length=100, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'contact')
        
