import uuid

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_ADMIN = 'admin'
ROLE_USER = 'user'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        Assigns auth token to created user
        """
        print('calling for action from inside')
        if not email:
            raise ValueError(_('Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        token = Token.objects.create(user=user)
        token.save()
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Creates non-superuser User.
        Extend this method in order to change values of default fields.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', ROLE_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Default user model. Created by admin.
    The only purpose for user is to be used in
    API authentication. Auth tokens are issued by superadmin.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    username = models.CharField(max_length=32, blank=False, null=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    )
    role = models.CharField(max_length=256,
                            choices=ROLE_CHOICES, default=ROLE_USER)

    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user '
                  'can log into this admin site.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )

    phone_number = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def auth_token(self):
        return Token.objects.get_or_create(user=self).key

    def assign_token(self):
        Token.objects.filter(user=self).delete()
        token = Token.objects.create(user=self)
        token.save()

    auth_token.short_description = 'Authentication token'

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']


@receiver(post_save, sender=User)
def handle_user_creation(sender, **kwargs):
    """
    Assign user with a token after creation.
    By default, tokens are only assigned on login.
    """
    if kwargs.get('created'):
        instance = kwargs.get('instance')
        token = Token.objects.create(user=instance)
        token.save()
