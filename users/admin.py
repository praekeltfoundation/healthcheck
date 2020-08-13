from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group, Permission

from .models import User as DefaultUser


def reassign_tokens(modeladmin, request, queryset):
    """
    (Re)assign auth tokens to selected users
    """
    for user in queryset:
        user.assign_token()
    reassign_tokens.short_description = (
        "Reassign authentication tokens for selected users"  # noqa: E501, E261
    )


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users.
    """

    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=False
    )

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = DefaultUser
        fields = (
            "username",
            "password",
        )


class UserForm(forms.ModelForm):
    """
    User read and update form.
    """

    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    def clean_password(self):
        # even though there is no way to change the password in this view,
        # we are still overriding the possible changed value with original value.
        return self.initial["password"]

    class Meta:
        model = DefaultUser
        fields = (
            "username",
            "password",
            "user_permissions",
            "role",
        )


class UserAdmin(BaseUserAdmin):
    """
    Slightly customized user model admin. Uses custom form.
    """

    form = UserForm
    add_form = UserCreationForm
    list_display = (
        "username",
        "auth_token",
        "date_joined",
    )
    list_filter = (
        "date_joined",
        "is_superuser",
    )
    readonly_fields = ("date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Permissions", {"fields": ("user_permissions",)}),
        ("Admin Type", {"fields": ("role", "is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password",),
            },  # noqa: E231, E501
        ),
    )

    actions = (reassign_tokens,)


admin.site.register(DefaultUser, UserAdmin)

admin.site.register(Permission)
admin.site.unregister(Group)
