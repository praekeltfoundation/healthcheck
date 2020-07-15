from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group
from django import forms


class UserForm(forms.ModelForm):
    """
    User CRUD form.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'first_name',
            'last_name', 'phone_number', 'role',
        )


def reassign_tokens(modeladmin, request, queryset):
    """
    (Re)assign auth tokens to selected users
    """
    for user in queryset:
        user.assign_token()
    reassign_tokens.short_description = "Mark selected stories as published"


class UserAdmin(admin.ModelAdmin):
    """
    Slightly customized user model admin. Uses custom form.
    """
    form = UserForm
    list_display = ('email', 'auth_token', 'date_joined',)
    actions = (reassign_tokens,)


admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
