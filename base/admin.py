from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import User, MenuItem, Rating, Complaint, Attendance
# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("username", "is_staff", "is_active","is_superuser","bits_id","hostel")
    list_filter = ("username", "is_staff", "is_active","is_superuser",)
    fieldsets = (
        (None, {"fields": ("username", "password","bits_id","hostel")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "password1","password2", "is_staff","bits_id","hostel",
                "is_active","is_superuser", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("username",)
    ordering = ("username",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(MenuItem)
admin.site.register(Rating)
admin.site.register(Complaint)
admin.site.register(Attendance)