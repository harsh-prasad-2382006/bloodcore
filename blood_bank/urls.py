"""
URL configuration for blood_bank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),

    path('donor-registration/',views.donor_registration,name='donor-registration'),
    path('receiver-registration/',views.receiver_registration,name='receiver-registration'),
    path('bloodbank-registration/',views.bloodbank_registration,name='bloodbank-registration'),

    path('sign-in/',views.sign_in,name='sign-in'),
    path('sign-out/',views.sign_out,name='sign-out'),

    path('donor-dashboard/',views.donor_dashboard,name='donor-dashboard'),
    path('receiver-dashboard/',views.receiver_dashboard,name='receiver-dashboard'),
    path('bloodbank-dashboard/',views.bloodbank_dashboard,name='bloodbank-dashboard'),


    path('donor-profile/',views.donor_profile,name='donor-profile'),
    path('schedule-donation/<int:id>',views.schedule_donation,name='schedule-donation'),
    path('donation-details/', views.donation_details, name='donation-details'),
    path('cancel-donation/<int:id>/', views.cancel_donation, name='cancel-donation'),
    path('edit-donor-profile/<int:id>',views.edit_donor_profile,name='edit-donor-profile'),


    path('bloodbank-profile/',views.bloodbank_profile,name='bloodbank-profile'),
    path('donation-request/',views.donation_request,name='donation-request'),
    path('receiver-request/',views.receiver_request,name='receiver-request'),
    path('update-donation-status/<int:id>',views.update_donation_status,name='update-donation-status'),
    path('edit-bloodbank-profile/<int:id>',views.edit_bloodbank_profile,name='edit-bloodbank-profile'),



    path('receiver-profile/',views.receiver_profile,name='receiver-profile'),
    path('receiving-details/',views.receiving_details,name='receiving-details'),
    path('schedule-request/<int:id>',views.schedule_request,name='schedule-request'),
    path('update-request-status/<int:id>/',views.update_request_status,name='update-request-status'),
    path('edit-receiver-profile/<int:id>',views.edit_receiver_profile,name='edit-receiver-profile'),


    path('forgot-password/',views.forgot_password,name='forgot-password'),
    path('verify-otp/',views.verify_otp,name='verify-otp'),
    path('reset-password/<int:user_id>/',views.reset_password,name='reset-password'),

    path("run-migrations/", views.run_migrations),  

]


