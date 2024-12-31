from django.db import models

import os
import uuid

from storages.backends.s3boto3 import S3Boto3Storage

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_unique_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('company_logos/', unique_filename)

class Company(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    company_admin_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)   
    password = models.CharField(max_length=255)  
    phone_no1 = models.CharField(max_length=15)
    phone_no2 = models.CharField(max_length=15, blank=True, null=True)   
   
    company_logo = models.ImageField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)


    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
          
         
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    QUALITY = 'quality'
    ENVIRONMENT = 'environment'
    HEALTH_AND_SAFETY = 'health_and_safety'
    ENERGY = 'energy'
    IMS = 'ims'

    PERMISSION_CHOICES = [
        (QUALITY, 'Quality'),
        (ENVIRONMENT, 'Environment'),
        (HEALTH_AND_SAFETY, 'Health and Safety'),
        (ENERGY, 'Energy'),
        (IMS, 'IMS'),
    ]

    permissions = models.ManyToManyField('Permission', blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.company_name

class Permission(models.Model):
    name = models.CharField(max_length=100, choices=Company.PERMISSION_CHOICES)
    
    def __str__(self):
        return self.get_name_display()
    
    
 
