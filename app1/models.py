from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator,MinValueValidator
from django.utils import timezone
# Create your models here.

blood_choice = [('a+', 'A+'), ('a-', 'A-'),
    ('b+', 'B+'), ('b-', 'B-'),
    ('ab+', 'AB+'), ('ab-', 'AB-'),
    ('o+', 'O+'), ('o-', 'O-'),
]

class Address(models.Model):
    building = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10,validators=[RegexValidator(regex = r'^\d{6}$',message = "Enter six digits pincode")])

    def __str__(self):
        return f"{self.building} {self.taluka}, {self.state} {self.city} - {self.pincode}"

class CustomUser(AbstractUser):
    is_donor = models.BooleanField(default=False)
    is_receiver = models.BooleanField(default=False)
    is_bloodbank = models.BooleanField(default=False)
    contact = models.CharField(max_length=10,validators=[RegexValidator(regex=r'^\d{10}$',message = "Contact number must be 10 digits")])
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Donor(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='donor_profile')
    dob = models.DateField(null=True)
    bloodgroup = models.CharField(max_length=3,choices = blood_choice,null=True)
    has_disease = models.BooleanField(default=False,null=False)
    last_donation_date = models.DateField(null=True,blank=True)
    weight = models.PositiveIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"



class Receiver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='receiver_profile')
    dob = models.DateField(null=True)
    bloodgroup = models.CharField(max_length=3,choices = blood_choice,null=True)
    # dob = models.DateField()
    # bloodgroup_needed = models.CharField(max_length=3, choices=blood_choice)
    # quantity_required = models.PositiveIntegerField(help_text="Quantity in milliliters (ml)")
    # request_status = models.CharField(max_length=20, default='Pending', choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class BloodBank(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='blood_bank_profile')
    blood_centre_name = models.CharField(max_length=255, verbose_name="Blood Centre Name")
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=15,unique=True,validators=[RegexValidator(regex=r'^[A-Za-z0-9]{15}$', message="License number must be 15 alphanumeric characters.")]
    )
    blood_inventory = models.JSONField(default=dict) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_centre_name}"
    
class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_bank = models.ForeignKey(BloodBank, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.donor.user.get_full_name()} - {self.scheduled_date}"
    
class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    receiver = models.ForeignKey('Receiver', on_delete=models.CASCADE)
    blood_bank = models.ForeignKey('BloodBank', on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    units_required = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateField(auto_now_add=True)
    required_at = models.DateField(null=True)

    def __str__(self):
        return f"{self.receiver.user.get_full_name()} requested {self.units_required} unit(s) of {self.blood_group}"