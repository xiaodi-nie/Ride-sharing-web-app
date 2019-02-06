from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone
import datetime


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    is_driver = models.BooleanField(
        'IsDriver', default=False)

    class Meta:
        verbose_name = 'User Profile'

    def __str__(self):
        return self.user


class Driver(models.Model):
    note = models.CharField('note', max_length=128, blank=True)
    # foreign key to User table
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver')

    class Meta:
        verbose_name = 'Driver Profile'

    def __str__(self):
        return self.pk


class Vehicle(models.Model):
    # one to one with Driver table
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='vehicle')
    note_driver = models.CharField('note_driver', max_length=128, blank=True)
    type = models.CharField('type', max_length=128, blank=True)
    plate_num = models.CharField('plate_num', max_length=128, blank=True)
    max_passenger = models.PositiveSmallIntegerField('max_passenger', default=0)

    class Meta:
        verbose_name = 'Vehicle Information'

    def __str__(self):
        return self.pk


class Trip(models.Model):
    owner_id = models.PositiveSmallIntegerField('owner_id', default=0)
    address = models.CharField('address', max_length=128, default=None)
    note = models.CharField('note', max_length=128, blank=True)
    time = models.DateTimeField('time', default=timezone.now())
    curr_passenger = models.PositiveSmallIntegerField('curr_passenger', default=0)
    is_confirm = models.BooleanField('is_confirm', default=False)
    driver_id = models.PositiveSmallIntegerField('driver_id', default=0)
    is_complete = models.BooleanField('is_complete', default=False)
    is_shareable = models.BooleanField('is_shareable', default=False)

    class Meta:
        verbose_name = 'Trip Information'

    def __str__(self):
        return self.owner_id


class TripSharerList(models.Model):

    user_id = models.PositiveSmallIntegerField('user_id', default=0)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='sharer_list')

    class Meta:
        verbose_name = 'TripSharer Information'

    def __str__(self):
        return self.tripsharerlist

