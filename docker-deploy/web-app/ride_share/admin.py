from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Driver, Vehicle, TripSharerList, Trip

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]


admin.site.register(User, UserProfileAdmin)
admin.site.register(Driver)
admin.site.register(Trip)
admin.site.register(Vehicle)
admin.site.register(TripSharerList)
