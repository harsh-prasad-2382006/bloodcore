from django.http import Http404
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from .forms import DonorForm,ReceiverForm,BloodBankForm
from .models import Donor,Receiver,CustomUser,BloodBank,Address,CustomUser,Donation,BloodRequest
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
import json
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta,datetime
from django.db.models import Count, Q


from django.http import HttpResponse
from django.core.management import call_command

def run_migrations(request):
    call_command("migrate")
    return HttpResponse("Migrations completed.")


# Create your views here.
def index(request):
    return render(request,'index.html')

#


from datetime import datetime

def donor_registration(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        dob = request.POST['dob']
        bloodgroup = request.POST['bloodgroup']
        weight = request.POST['weight']
        has_disease = request.POST.get('has_disease', False) == 'on'
        last_donation_date = request.POST.get('last_donation_date', None)
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('donor-registration')

        if password != confirm_password:
            messages.error(request, "Password does not match")
            return redirect('donor-registration')

        try:
            user = CustomUser.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                contact=contact,
                email=email,
                password=password,
                is_donor=True
            )

            last_date = None
            if last_donation_date:
                last_date = datetime.strptime(last_donation_date, '%Y-%m-%d').date()

            donor = Donor.objects.create(
                user=user,
                dob=dob,
                has_disease=has_disease,
                bloodgroup=bloodgroup,
                weight=weight,
                last_donation_date=last_date
            )

            send_mail(
                'Registration Successful Mail',
                f'Thankyou {user.first_name} for successfully registering to our website',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            return redirect('sign-in')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('donor-registration')

    return render(request, 'donor_registration.html')



def receiver_registration(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        dob = request.POST['dob']
        bloodgroup = request.POST['bloodgroup']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('receiver-registration')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('receiver-registration')
        else:
            user = CustomUser.objects.create_user(username = email,first_name=first_name,last_name = last_name,contact = contact,email=email,password=password,is_receiver = True)
            user.save()

            receiver= Receiver.objects.create(user=user,dob=dob,bloodgroup=bloodgroup)
            receiver.save()

            send_mail(
                'Registration Successful Mail',
                f'Thankyou {user.first_name} for successfully registering to our website',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            return redirect('sign-in')
    return render(request,'receiver_registration.html')



def bloodbank_registration(request):
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    if request.method == 'POST':
        email = request.POST['email'].strip()
        contact = request.POST['contact'].strip()
        blood_centre_name = request.POST['blood_centre_name'].strip()
        license_number = request.POST['license_number'].strip()
        confirm_password = request.POST['confirm_password']
        password = request.POST['password']

        building = request.POST['building'].strip()
        taluka = request.POST['taluka'].strip()
        state = request.POST['state'].strip()
        city = request.POST['city'].strip()
        pincode = request.POST['pincode'].strip()

        if password != confirm_password:
            messages.error(request, "Password does not match")
            return redirect('bloodbank-registration')
        
        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('bloodbank-registration')
        
        if BloodBank.objects.filter(license_number=license_number).exists():
            messages.error(request, "License number already registered.")
            return redirect('bloodbank-registration')
            
      
        blood_inventory = {}
        for group in blood_groups:
            key = f"inventory_{group}"
            value = request.POST.get(key, 0)
            print(f"Group: {group}, Inventory: {value}") 
            try:
                blood_inventory[group] = int(value) 
            except (ValueError, TypeError):
                blood_inventory[group] = 0  

        print(f"Final Blood Inventory: {blood_inventory}")

        try:
            user = CustomUser.objects.create_user(username=email, contact=contact, email=email, password=password, is_bloodbank=True)
            address = Address.objects.create(building=building, state=state, city=city, taluka=taluka, pincode=pincode)
            bloodbank = BloodBank.objects.create(
                user=user,
                address=address,
                blood_centre_name=blood_centre_name,
                license_number=license_number,
                blood_inventory=blood_inventory
            )

            send_mail(
                'Registration Successful Mail',
                f"Thank you, {bloodbank.blood_centre_name}, for registering. You can now manage donations and requests.",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )

            messages.success(request, "Registration successful! Please log in.")
            return redirect('sign-in')
        
        except Exception as e:
            messages.error(request, f"An error occurred during registration: {str(e)}")
            return redirect('bloodbank-registration')
        
    context = {
        'bloodgroups': blood_groups
    }

    return render(request, 'bloodbank_registration.html', context)



def sign_in(request):
    if request.method=='POST':
        form = AuthenticationForm(request=request,data = request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                if user.is_donor:
                    login(request,user)
                    request.session.set_expiry(0)
                    return redirect('donor-dashboard')
                elif user.is_receiver:
                    login(request,user)
                    request.session.set_expiry(0)
                    return redirect('receiver-dashboard')
                elif user.is_bloodbank:
                    login(request,user)
                    request.session.set_expiry(0)
                    return redirect('bloodbank-profile')
                else:
                    messages.error(request,"User does not exist with a recognized role.")
                    return redirect('sign-in')
        else:
            messages.error(request, "Invalid Credentials") 
    else:
        form = AuthenticationForm()
    context = {
        'form':form
    }
    return render(request,'sign_in.html',context)


def sign_out(request):
    logout(request)
    return redirect('index')


def donor_dashboard(request):
    donor = Donor.objects.all()
    bloodbanks =[]
    pincode = request.GET.get('pincode')
    if pincode:
        bloodbanks = BloodBank.objects.filter(address__pincode__icontains=pincode)

    context = {
        'donor':donor,
        'bloodbanks':bloodbanks,
        'user_type': 'donor',
    }
    return render(request,'donor_dashboard.html',context)

@login_required
def donor_profile(request):
    donor = Donor.objects.get(user = request.user)
    if donor.last_donation_date:
        next_eligible_date = donor.last_donation_date + timedelta(days=90)
    else:
        next_eligible_date = None 
    scheduled_date = Donation.objects.filter(donor=donor).order_by('-scheduled_date').first()
    context = {
        'donor':donor,
        'next_eligible_date':next_eligible_date,
        'date':scheduled_date
    }
    return render(request,'donor_profile.html',context)


from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from django.utils.timezone import now

def schedule_donation(request, id):
    donor = Donor.objects.get(user=request.user)
    bloodbank = BloodBank.objects.get(id=id)

    existing_donation = Donation.objects.filter(donor=donor, status__in=['pending', 'accepted']).first()
    if existing_donation:
        messages.error(request, "You have already scheduled a donation. Please wait for it to be completed or rejected before scheduling another.")
        return redirect('donor-profile')
    if donor.last_donation_date:
        next_eligible_date = donor.last_donation_date + timedelta(days=90)
    else:
        next_eligible_date = date.today()



    if request.method == 'POST':
        schedule_date = request.POST['donation_date']
        schedule_time = request.POST['donation_time']
        selected_date = date.fromisoformat(schedule_date)

        if selected_date < next_eligible_date:
            messages.error(request, f"You are not eligible to donate before {next_eligible_date.strftime('%d-%m-%Y')}.")
            return redirect('schedule-donation', id=id)

        if donor.weight <= 50:
            messages.error(request,'Your weight is less than 50kg you are unable to donate blood')
            return redirect('donor-profile')
        
        if donor.has_disease: 
            messages.error(request, "You are not eligible to donate blood due to a health condition.")
            return redirect('donor-profile')
    
        donation = Donation.objects.create(
            donor=donor,
            blood_bank=bloodbank,
            scheduled_date=schedule_date,
            scheduled_time=schedule_time,
            status='pending'
        )
        donation.save()
        send_mail(
            'Donation Date Scheduled',
            f"""Dear {donor.user.first_name},\n\n
            You have successfully scheduled your blood donation for {schedule_date} at {schedule_time}.
            Please wait until your donation status is confirmed.""",
            settings.EMAIL_HOST_USER,
            [donor.user.email],
            fail_silently=False
        )
        messages.success(request,"You have successfully applied for donation")
        return redirect('donation-details')

    context = {
        'bloodbank': bloodbank,
        'next_eligible_date': next_eligible_date
    }

    return render(request, 'schedule_donation.html', context)



def donation_details(request):
    donor = Donor.objects.get(user=request.user)
    last_donation_date = donor.last_donation_date
    if last_donation_date:
        next_eligible_date = last_donation_date + timedelta(days=90)
    else:
        next_eligible_date = None

    donation = Donation.objects.filter(donor=donor).order_by('-scheduled_date').first()

    context = {
        'donor': donor,
        'donation': donation,
        'last_donation_date': last_donation_date,
        'next_eligible_date': next_eligible_date,
    }
    return render(request, 'donation_details.html', context)



def cancel_donation(request, id):
    donation = get_object_or_404(Donation, id=id, donor__user=request.user)

    if request.method == "POST":
        donation.delete()
        messages.success(request, "Your donation has been successfully cancelled.")

    return redirect('donation-details')  



def edit_donor_profile(request, id):
    donor = Donor.objects.get(id=id)
    user = donor.user  # Get the actual CustomUser instance

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        dob = request.POST['dob']
        bloodgroup = request.POST['bloodgroup']
        weight = request.POST['weight']
        has_disease = request.POST.get('has_disease', False) == 'on'

        user.username = email
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.contact = contact
        user.is_donor = True
        user.save()

        donor.dob = dob
        donor.has_disease = has_disease
        donor.bloodgroup = bloodgroup
        donor.weight = weight
        donor.save()

        messages.success(request, "Your profile has been updated successfully.")
        return redirect('donor-profile')

    context = {
        'donor': donor
    }
    return render(request, 'edit_donor_profile.html', context)


def receiver_dashboard(request):
    bloodbanks = []
    pincode = request.GET.get('pincode')

    if pincode:
        bloodbanks = BloodBank.objects.filter(address__pincode=pincode)

    context = {
        'bloodbanks': bloodbanks,
        'pincode': pincode
    }
    return render(request, 'receiver_dashboard.html', context)



def receiver_profile(request):
    receiver = Receiver.objects.get(user=request.user)
    context = {
        'receiver':receiver
    }
    return render(request,'receiver_profile.html',context)



def receiving_details(request):
    receiver = Receiver.objects.get(user=request.user)
    selected_status = request.GET.get('status')  # Get selected filter from query params

    blood_requests = BloodRequest.objects.filter(receiver=receiver).order_by('-requested_at')
    if selected_status and selected_status != 'all':
        blood_requests = blood_requests.filter(status=selected_status)

    context = {
        'blood_requests': blood_requests,
        'selected_status': selected_status or 'all'
    }
    return render(request, 'receiving_details.html', context)



def schedule_request(request,id):
    receiver = Receiver.objects.get(user = request.user)
    bloodbank = BloodBank.objects.get(id=id)

    pending_request = BloodRequest.objects.filter(receiver=receiver, status='pending').first()
    if pending_request:
        messages.warning(request, "You already have a pending blood request. Please wait for it to be processed before making a new one.")
        return redirect('receiving-details')
    if request.method == "POST":
        required_date = request.POST.get('required_date')
        blood_group = request.POST.get('blood_group')
        quantity = request.POST.get('quantity')

        bloodrequest = BloodRequest.objects.create(receiver = receiver,blood_bank = bloodbank,blood_group = blood_group,units_required = quantity,required_at = required_date)
        bloodrequest.save()

        send_mail(
            'Request from you for blood',
            f"""Dear {receiver.user.first_name},\n
            We have receive your blood request for blood group {blood_group}.
            Please wait until your request status is confirmed.""",
            settings.EMAIL_HOST_USER,
            [receiver.user.email],
            fail_silently=False
        )
        messages.success(request,"You have successfully submitted a blood request.")
        return redirect('receiving-details')
    context = {
        'receiver':receiver,
        'bloodbank':bloodbank
    }
    return render(request,'schedule_request.html',context)



def edit_receiver_profile(request, id):
    receiver = Receiver.objects.get(id=id)
    user = receiver.user

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        contact = request.POST['contact']
        dob = request.POST['dob']
        bloodgroup = request.POST['bloodgroup']

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email  
        user.contact = contact
        user.save()

        # Update receiver details
        receiver.dob = dob
        receiver.bloodgroup = bloodgroup
        receiver.save()

        messages.success(request, "Your profile has been updated successfully.")
        return redirect('receiver-profile') 

    context = {
        'receiver': receiver,
    }
    return render(request, 'edit_receiver_profile.html', context)



def bloodbank_dashboard(request):
    bloodbank = BloodBank.objects.get(user=request.user)

    total_donations = Donation.objects.filter(blood_bank=bloodbank, status='accepted').count()
    pending_donations = Donation.objects.filter(blood_bank=bloodbank, status='pending').count()
    accepted_donations = Donation.objects.filter(blood_bank=bloodbank, status='accepted').count()
    rejected_donations = Donation.objects.filter(blood_bank=bloodbank, status='rejected').count()

    total_blood_requests = BloodRequest.objects.filter(blood_bank=bloodbank).count()
    pending_blood_requests = BloodRequest.objects.filter(blood_bank=bloodbank, status='pending').count()
    approved_blood_requests = BloodRequest.objects.filter(blood_bank=bloodbank, status='approved').count()
    rejected_requests = BloodRequest.objects.filter(blood_bank=bloodbank, status='rejected').count()

    context = {
        'bloodbank': bloodbank,
        'total_donations': total_donations,
        'pending_donations': pending_donations,
        'accepted_donations': accepted_donations,
        'rejected_donations': rejected_donations,
        'total_blood_requests': total_blood_requests,
        'pending_blood_requests': pending_blood_requests,
        'approved_blood_requests': approved_blood_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'bloodbank_dashboard.html', context)

def bloodbank_profile(request):
    bloodbank = BloodBank.objects.get(user = request.user)
    context={
        'bloodbank':bloodbank
    }
    return render(request,'bloodbank_profile.html',context)



def donation_request(request):
    bloodbank = BloodBank.objects.get(user=request.user)
    bloodgroup = request.GET.get('bloodgroup', '')
    donations = Donation.objects.filter(blood_bank=bloodbank).order_by('-scheduled_date')
    if bloodgroup:
        donations = donations.filter(donor__bloodgroup__iexact=bloodgroup)
    else:
        donations = Donation.objects.filter(blood_bank=bloodbank).order_by('-scheduled_date')

    context = {
        'donations': donations,
        'selected_bloodgroup': bloodgroup,
    }
    return render(request, 'donation_request.html', context)


def receiver_request(request):
    bloodbank = BloodBank.objects.get(user=request.user)
    requests = BloodRequest.objects.filter(blood_bank = bloodbank)
    context = {
        'requests':requests
    }
    return render(request,'receiver_request.html',context)


def update_request_status(request, id):
    try:
        blood_request = BloodRequest.objects.get(id=id)
        action = request.GET.get('q') 
        blood_bank = blood_request.blood_bank
        blood_group = blood_request.blood_group
        units_requested = blood_request.units_required
        receiver_email = blood_request.receiver.user.email
        receiver_name = blood_request.receiver.user.first_name

        if action == '0': 
            current_units = blood_bank.blood_inventory.get(blood_group, 0)

            if current_units >= units_requested:
                blood_bank.blood_inventory[blood_group] -= units_requested
                blood_bank.save()
                blood_request.status = 'approved'
                blood_request.save()

                send_mail(
                    'Blood Request Approved',
                    f"""Dear {receiver_name},\n\nYour request for {units_requested} units of {blood_group} blood has been approved by 
{blood_bank.blood_centre_name} . Please visit the center at your earliest convenience.""",
                    settings.EMAIL_HOST_USER,
                    [receiver_email],
                    fail_silently=False
                )

                messages.success(request, f"Request approved and {units_requested} units of {blood_group} deducted.")
            else:
                messages.error(request, f"Not enough {blood_group} blood units available.")
                return redirect('receiver-request')

        else:  
            blood_request.status = 'rejected'
            blood_request.save()

            send_mail(
                'Blood Request Rejected',
                f'Dear {receiver_name},\n\nWe regret to inform you that your request for {units_requested} units of {blood_group} blood has been rejected by {blood_bank.blood_centre_name} due to limited availability or other reasons.',
                settings.EMAIL_HOST_USER,
                [receiver_email],
                fail_silently=False
            )

            messages.info(request, "Request has been rejected.")

    except BloodRequest.DoesNotExist:
        messages.error(request, "Request not found.")

    return redirect('receiver-request')


def update_donation_status(request,id):
    try:
        donation = Donation.objects.get(id=id)
        var = request.GET.get('q')
        if var == '0':
            donation.status = 'accepted'
        else:
            donation.status = 'rejected'
        donation.save()

        if donation.status == 'rejected':
                send_mail(
                'Donation Date Rejected',
                f"""Dear {donation.donor.user.first_name}, Your donation request has been cancelled""",
                settings.EMAIL_HOST_USER,
                [donation.donor.user.email],
                fail_silently=False
            )
        else:
            send_mail(
                'Donation Date Confirmed',
                f"""Dear {donation.donor.user.first_name}, You have requested for blood donation on {donation.scheduled_date},
Your donation is successfully scheduled on {donation.scheduled_date}""",
                settings.EMAIL_HOST_USER,
                [donation.donor.user.email],
                fail_silently=False
            )

        messages.success(request, "Donation request accepted successfully.")
    except Donation.DoesNotExist:
        messages.error(request, "Donation request not found.")
    return redirect('donation-request')


def edit_bloodbank_profile(request, id):
    try:
        bloodbank = BloodBank.objects.get(id=id)
        user = bloodbank.user
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    except BloodBank.DoesNotExist:
        raise Http404("Blood Bank not found")

    if request.method == 'POST':
      
        bloodbank.blood_centre_name = request.POST.get('blood_centre_name', bloodbank.blood_centre_name)
        user.contact = request.POST.get('contact', user.contact)

        address = bloodbank.address
        address.building = request.POST.get('building', address.building)
        address.city = request.POST.get('city', address.city)
        address.state = request.POST.get('state', address.state)
        address.taluka = request.POST.get('taluka', address.taluka)
        address.pincode = request.POST.get('pincode', address.pincode)

        address.save()

        inventory = {}
        for group in blood_groups:
            qty = request.POST.get(f'inventory_{group}')
            try:
                inventory[group] = int(qty) if qty else 0 
            except ValueError:
                inventory[group] = 0 

        bloodbank.blood_inventory = inventory

        user.save()
        bloodbank.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('bloodbank-profile')

    context = {
        'bloodbank': bloodbank,
        'blood_groups': blood_groups
    }
    return render(request, 'edit_bloodbank_profile.html', context)


import random
def generate_otp():
    otp = str(random.randrange(100000,999999))
    return otp

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['request_user'] = user.id

            send_mail(
                subject='Password Reset OTP - BloodCore',
                message=f'Hello {user.first_name},\n\nYour OTP for resetting your BloodCore password is: {otp}\n\nIf you didn’t request this, please ignore this email.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email. Please check your inbox.')
            return redirect('verify-otp')

        except CustomUser.DoesNotExist:
            messages.error(request, 'This email is not registered with BloodCore.')
    
    return render(request, 'forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_stored = request.session.get('otp')
        user_id = request.session.get('request_user')

        if otp_stored and otp_entered == otp_stored:
            if user_id:
                del request.session['otp']
                return redirect('reset-password', user_id=user_id)
            else:
                messages.error(request, "Session expired, please request a new OTP.")
                return redirect('forgot-password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify-otp')

    return render(request, 'verify_otp.html')


def reset_password(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('forgot-password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset-password', user_id=user.id)

        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('reset-password', user_id=user.id)

        user.set_password(new_password)
        user.save()
        request.session.flush()

        send_mail(
            'Password Reset Confirmation',
            'Your password has been successfully reset. You can now log in with your new password.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(request, "Password reset successfully. Please log in.")
        return redirect('sign-in') 

    return render(request, 'reset_password.html')