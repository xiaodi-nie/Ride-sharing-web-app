from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, Vehicle, Driver, TripSharerList, Trip
from django.contrib import auth
# from .forms import RegistrationForm, LoginForm
from .forms import RegistrationForm, LoginForm, ProfileForm, PwdChangeForm, DriverRegistrationForm, RequestCarForm, \
    UpdateCurrentTripForm, ShareCarForm, JoinRideForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from datetime import datetime, timedelta

def home(request):
    return render(request, 'ride_share/home.html')

def register(request):
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']

            # 使用内置User自带create_user方法创建用户，不需要使用save()
            user = User.objects.create_user(username=username, password=password, email=email)

            # 如果直接使用objects.create()方法后不需要使用save()
            user_profile = UserProfile(user=user)
            user_profile.save()

            return HttpResponseRedirect("/login/")

    else:
        form = RegistrationForm()

    return render(request, 'ride_share/registration.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('ride_share:profile', args=[user.id]))

            else:
                # 登陆失败
                  return render(request, 'ride_share/login.html', {'form': form,
                               'message': 'Wrong password. Please try again.'})
    else:
        form = LoginForm()

    return render(request, 'ride_share/login.html', {'form': form})

@login_required
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'ride_share/profile.html', {'user': user})
@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

@login_required
def profile_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()



            user_profile.save()

            return HttpResponseRedirect(reverse('ride_share:profile', args=[user.id]))
    else:
        default_data = {'first_name': user.first_name, 'last_name': user.last_name,
                         }
        form = ProfileForm(default_data)

    return render(request, 'ride_share/profile_update.html', {'form': form, 'user': user})

@login_required
def pwd_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = PwdChangeForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data['old_password']
            username = user.username

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                new_password = form.cleaned_data['password2']
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect("/accounts/login/")

            else:
                return render(request, 'ride_share/pwd_change.html', {'form': form,
        'user': user, 'message': 'Old password is wrong. Try again'})
    else:
        form = PwdChangeForm()

    return render(request, 'ride_share/pwd_change.html', {'form': form, 'user': user})

@login_required
def register_driver(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':

        form = DriverRegistrationForm(request.POST)
        if user_profile.is_driver:

            return render(request, 'ride_share/register_driver.html', {'form': form, 'user':user,
                                                                       'message': 'You are already a driver'})

        if form.is_valid():
            vehicle_type = form.cleaned_data['vehicle_type']
            plate_num = form.cleaned_data['plate_num']
            max_passenger = form.cleaned_data['max_passenger']
            note = form.cleaned_data['note']

            # create a driver object
            driver = Driver(user=user, note=note)
            driver.save()
            # create a vehicle object and build one to one relation with driver
            vehicle = Vehicle(driver=driver, type=vehicle_type, plate_num=plate_num, max_passenger=max_passenger,
                              note_driver=note)
            vehicle.save()

            user_profile.is_driver = True
            user_profile.save()

            return HttpResponseRedirect(reverse('ride_share:profile', args=[user.id]))

    else:
        form = DriverRegistrationForm()

    return render(request, 'ride_share/register_driver.html', {'form': form})


@login_required
def request_car(request, pk):
    user = get_object_or_404(User, pk=pk)
    # user_profile = get_object_or_404(UserProfile, user=user)
    if request.method == 'POST':
        form = RequestCarForm(request.POST)
        trip = Trip.objects.filter((Q(owner_id=pk)&Q(is_complete=False)) | (Q(driver_id=pk) & Q(is_complete=False)))
        tripsharer = TripSharerList.objects.filter(user_id=pk)
        queryShareExit = False
        for item in tripsharer:
            item_trip = item.trip

            if not item_trip.is_complete:
                queryShareExit = True

        if trip.exists() or queryShareExit:
            return render(request, 'ride_share/request_car.html',
                          {'form': form, 'user': user,
                           'message': 'You can not request a ride because you have an incomplete trip.'})

        if form.is_valid():

            address = form.cleaned_data['address']
            curr_passenger = form.cleaned_data['passenger_num']
            note = form.cleaned_data['note']
            time = form.cleaned_data['time']
            is_shareable = form.cleaned_data['is_shareable']

            newtrip = Trip(address=address, time=time,  note=note, owner_id=pk, curr_passenger=curr_passenger,
                           is_shareable=is_shareable)
            newtrip.save()
            if not newtrip.is_confirm:
                # return HttpResponseRedirect(reverse('ride_share:current_trip', args=[newtrip]))
                return render(request, 'ride_share/current_trip.html',
                              {'form': form, 'newtrip': newtrip})
            driver_id = newtrip.driver_id
            driver_profile = get_object_or_404(User, pk=driver_id)
            vehicle = get_object_or_404(Vehicle, pk=driver_profile.driver.pk)
            # return HttpResponseRedirect(reverse('ride_share:current_trip', args=[newtrip, driver_profile, vehicle]))
            return render(request, 'ride_share/current_trip.html',
                          {'form': form, 'newtrip': newtrip, 'driver_profile': driver_profile, 'vehicle': vehicle})
    else:
        form = RequestCarForm()

    return render(request, 'ride_share/request_car.html', {'form': form, 'user': user})


def find_current_trip(pk):
    trip_owner = Trip.objects.filter(owner_id=pk, is_complete=False)

    trip_driver = Trip.objects.filter(driver_id=pk, is_complete=False)

    tripsharer = TripSharerList.objects.filter(user_id=pk)

    if trip_owner.exists():
        return trip_owner.all()[:1].get()
    if trip_driver.exists():
        return trip_driver.all()[:1].get()
    if tripsharer.exists():
        trip_sharer = None
        for item in tripsharer:
            item_trip = item.trip
            if not item_trip.is_complete:
                trip_sharer = item.trip
        if trip_sharer:
            return trip_sharer
    return None


def current_trip(request, pk):
    if request.method == 'POST':
        trip_driver = Trip.objects.filter(driver_id=pk, is_complete=False)

        if trip_driver.exists:
            current_trip_driver = trip_driver.all()[:1].get()
            current_trip_driver.is_complete = True
            current_trip_driver.save()
            return render(request, 'ride_share/confirm_success.html',
                          {'message': 'Trip completed successfully'})
        return render(request, 'ride_share/confirm_success.html',
                      {'message': 'You are not the driver of this trip'})
    else:
        trip_owner = Trip.objects.filter(owner_id=pk, is_complete=False)

        trip_driver = Trip.objects.filter(driver_id=pk, is_complete=False)

        tripsharer = TripSharerList.objects.filter(user_id=pk)
        trip_sharer = None
        for item in tripsharer:
            item_trip = item.trip

            if not item_trip.is_complete:
                trip_sharer = item.trip
        if trip_owner.exists():
            if not trip_owner.all()[:1].get().is_confirm:
                # return HttpResponseRedirect(reverse('ride_share:current_trip', args=[newtrip]))
                return render(request, 'ride_share/current_trip.html',
                              { 'newtrip': trip_owner.all()[:1].get() })
            driver_id = trip_owner.all()[:1].get().driver_id
            driver_profile = get_object_or_404(User, pk=driver_id)
            vehicle = get_object_or_404(Vehicle, pk=driver_profile.driver.pk)
            # return HttpResponseRedirect(reverse('ride_share:current_trip', args=[newtrip, driver_profile, vehicle]))
            return render(request, 'ride_share/current_trip.html',
                          { 'newtrip': trip_owner.all()[:1].get(), 'driver_profile': driver_profile, 'vehicle': vehicle})
        elif trip_driver.exists():
            driver_curr_trip = trip_driver.all()[:1].get()
            driver_id = pk
            driver_profile = get_object_or_404(User, pk=driver_id)
            vehicle = get_object_or_404(Vehicle, pk=driver_profile.driver.pk)
            return render(request, 'ride_share/current_trip.html',
                          {'newtrip': driver_curr_trip, 'driver_profile': driver_profile, 'vehicle': vehicle})
        elif trip_sharer:
            if not trip_sharer.is_confirm:
                # return HttpResponseRedirect(reverse('ride_share:current_trip', args=[newtrip]))
                return render(request, 'ride_share/current_trip.html',
                              { 'newtrip': trip_sharer})
            driver_id = trip_sharer.driver_id
            driver_profile = get_object_or_404(User, pk=driver_id)
            vehicle = get_object_or_404(Vehicle, pk=driver_profile.driver.pk)
            return render(request, 'ride_share/current_trip.html',
                          { 'newtrip': trip_sharer, 'driver_profile': driver_profile, 'vehicle': vehicle})
        else:
            return render(request, 'ride_share/current_trip.html',
                          {'message': 'You currently have no incomplete trip.'})


@login_required
def current_trip_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_profile = get_object_or_404(UserProfile, user=user)
    current_trip = find_current_trip(pk)
    if request.method == "POST":
        form = UpdateCurrentTripForm(request.POST)

        if current_trip and current_trip.is_confirm:
            return render(request, 'ride_share/current_trip_update.html',
                          {'message': 'Your trip is already confirmed by driver and can not be changed.'})
        if not current_trip.owner_id != pk:
            return render(request, 'ride_share/current_trip_update.html',
                          {'message': 'Only owner of this trip can modify request.'})

        if form.is_valid():
            current_trip.address = form.cleaned_data['address']
            current_trip.curr_passenger = form.cleaned_data['passenger_num']
            current_trip.note = form.cleaned_data['note']
            current_trip.time = form.cleaned_data['time']
            current_trip.is_shareable = form.cleaned_data['is_shareable']
            current_trip.save()
            return HttpResponseRedirect(reverse('ride_share:current_trip', args=[user.id]))
    else:
        default_data = {'address': current_trip.address, 'passenger_num': current_trip.curr_passenger,
                        'note': current_trip.note, 'time': current_trip.time}
        form = UpdateCurrentTripForm(default_data)

    return render(request, 'ride_share/current_trip_update.html', {'form': form, 'trip': current_trip})


@login_required
def driver_search_order(request, pk):
    user = get_object_or_404(User, pk=pk)
    curr_trip = find_current_trip(pk)
    driver_id = user.driver.id
    vehicle = get_object_or_404(Vehicle, pk=driver_id)
    trips = Trip.objects.filter(is_confirm=False, curr_passenger__lte=vehicle.max_passenger,
                                note__exact=vehicle.note_driver)
    if request.method == 'POST':
        trip_id = request.POST.get('trip')
        confirm_trip = Trip.objects.get(pk=trip_id)
        confirm_trip.is_confirm = True
        confirm_trip.driver_id = pk
        confirm_trip.save()
        owner = User.objects.get(pk=confirm_trip.owner_id)
        owner_email = owner.email
        send_mail('Trip confirmed', 'Your trip is confirmed by a driver, you can check driver and vehicle info in the '
                                    '"Current Trip" tab', 'allofprogramming551@gmail.com',
                  [owner_email], fail_silently=False)
        sharer_list = confirm_trip.sharer_list.all()
        for sharer in sharer_list:
            sharer_email = User.objects.get(pk=sharer.user_id).email
            send_mail('Trip confirmed', 'Your trip is confirmed by a driver, you can check driver and vehicle info '
                                        'in the "Current Trip" tab', 'allofprogramming551@gmail.com',
                      [sharer_email], fail_silently=False)
        return render(request, 'ride_share/confirm_success.html',
                      {'message': 'Trip confirmed successfully, emails were sent to passengers.'})

    else:
        if curr_trip:
            return render(request, 'ride_share/driver_search_order.html',
                          {'message': 'You currently have incomplete trip'})
    return render(request, 'ride_share/driver_search_order.html', {'trips': trips})


@login_required
def share_car(request, pk):
    user = get_object_or_404(User, pk=pk)
    # user_profile = get_object_or_404(UserProfile, user=user)
    if request.method == 'POST':
        form = ShareCarForm(request.POST)

        curr_trip = find_current_trip(pk)

        if curr_trip:
            return render(request, 'ride_share/share_car.html',
                          {'form': form, 'user': user,
                           'message': 'You can not share a ride because you have an incomplete trip.'})

        if form.is_valid():

            address = form.cleaned_data['address']
            start_time = form.cleaned_data['start_time']
            final_time = form.cleaned_data['final_time']
            if final_time - start_time <= timedelta(minutes=1):
                return render(request, 'ride_share/share_car.html',
                              {'form': form, 'user': user,
                               'message': 'Time interval invalid. Please enter again'})
            trip_list = Trip.objects.filter(is_confirm=False, time__gte=start_time, time__lte=final_time,
                                         address=address, is_shareable=True)

            if not trip_list.exists():
                return render(request, 'ride_share/share_car.html',
                              {'form': form, 'user': user,
                               'message': 'There are no available open rides that match your request'})
            else:
                return render(request, 'ride_share/join_ride.html', {'trip_list': trip_list, 'user': user})
                #return HttpResponseRedirect(reverse('ride_share:join_ride', args=[user.id, trip_list, user]))
    else:
        form = ShareCarForm()
    return render(request, 'ride_share/share_car.html', {'form': form, 'user': user})
    #return render(request, 'ride_share/join_ride.html', {'user': user, 'form': form2})


@login_required
def join_ride(request, pk, trip_id):
    user = get_object_or_404(User, pk=pk)
    # current_trip = find_current_trip(pk)
    # driver_id = user.driver.id
    # vehicle = get_object_or_404(Vehicle, pk=driver_id)
    # trips = Trip.objects.filter(is_confirm=False, curr_passenger__lte=vehicle.max_passenger,
    #                             note__exact=vehicle.note_driver)
    if request.method == 'POST':
        form = JoinRideForm(request.POST)
        if form.is_valid():
            curr_passenger = form.cleaned_data['passenger_num']
            #trip_id = request.POST.get('trip')
            trip = Trip.objects.get(pk=trip_id)
            trip.curr_passenger += curr_passenger
            sharer = TripSharerList(user_id=pk, trip=trip)
            sharer.save()
            return render(request, 'ride_share/confirm_success.html',
                    {'message': 'Join ride success. You can check your current trip info in "Current Trip" tab'})
    else:
        form = JoinRideForm()
        return render(request, 'ride_share/join_ride.html', {'form': form})


def past_trip(request, pk):
    trips_nonshare = Trip.objects.filter((Q(owner_id=pk) | Q(driver_id=pk)) & Q(is_confirm=True))
    tripsharer = TripSharerList.objects.filter(user_id=pk)
    trips = []
    trips_share = []

    if (not trips_nonshare.exists()) and (not tripsharer.exists()):
        return render(request, 'ride_share/past_trip.html',
                     {'message': 'You have no past trips.'})
    else:
        if trips_nonshare.exists():
            for trip in trips_nonshare:
                driver_id = trip.driver_id
                driver_profile_one = get_object_or_404(User, pk=driver_id)
                vehicle_one = get_object_or_404(Vehicle, pk=driver_profile_one.driver.pk)

                tup1 = (trip, driver_profile_one, vehicle_one)
                trips.append(tup1)
        if tripsharer.exists():
            for sharer in tripsharer:
                if sharer.trip.is_confirm:
                    driver_id = sharer.driver_id
                    driver_profile_share_one = get_object_or_404(User, pk=driver_id)
                    vehicle_share_one = get_object_or_404(Vehicle, pk=driver_profile_share_one.driver.pk)
                    tup2 = (sharer.trip, driver_profile_share_one, vehicle_share_one)

                    trips_share.append(tup2)


        return render(request, 'ride_share/past_trip.html',
                     {'trips': trips, 'trips_share': trips_share})