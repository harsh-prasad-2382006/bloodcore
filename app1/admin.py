from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Donor, Receiver, BloodBank, Donation, BloodRequest

# CustomUser Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [i.name for i in CustomUser._meta.fields]  # Explicit field names

# Donor Admin
class DonorAdmin(admin.ModelAdmin):
    model = Donor
    list_display = [i.name for i in Donor._meta.fields]  # Explicit field names

# Receiver Admin
class ReceiverAdmin(admin.ModelAdmin):
    model = Receiver
    list_display = [i.name for i in Receiver._meta.fields]  # Explicit field names

# BloodBank Admin
class BloodBankAdmin(admin.ModelAdmin):
    model = BloodBank
    list_display = [i.name for i in BloodBank._meta.fields]  # Explicit field names

# BloodBank Admin
class DonationAdmin(admin.ModelAdmin):
    model = Donation
    list_display = [i.name for i in Donation._meta.fields]  # Explicit field names


class BloodRequestAdmin(admin.ModelAdmin):
    model = BloodRequest
    list_display = [i.name for i in BloodRequest._meta.fields]  # Explicit field names

# Register your models with the admin interface
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Donor, DonorAdmin)
admin.site.register(Receiver, ReceiverAdmin)
admin.site.register(BloodBank, BloodBankAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(BloodRequest, BloodRequestAdmin)
