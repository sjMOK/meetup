from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=45)
    name = models.CharField(max_length=45)
    email = models.EmailField()
    user_type = models.ForeignKey('UserType', models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'

    # objects = CustomUserManager()

    class Meta:
        db_table = 'user'


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    possible_duration = models.IntegerField()

    class Meta:
        db_table = 'user_type'
