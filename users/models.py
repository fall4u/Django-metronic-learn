# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your models here.




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickName = models.CharField(max_length=128, blank=True)
    avatarUrl = models.CharField(max_length=128,blank=True)
    gender = models.CharField(max_length=128,blank=True)
    city = models.CharField(max_length=128,blank=True)
    province = models.CharField(max_length=128,blank=True)
    country = models.CharField(max_length=128,blank=True)
    language = models.CharField(max_length=128,blank=True)




class Address(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    provinceId = models.PositiveIntegerField(default = 0)
    cityId = models.PositiveIntegerField(default = 0)
    districtId = models.PositiveIntegerField(default =0)
    contact = models.CharField(max_length=128, blank=True)
    address = models.CharField(max_length=128, blank=True)
    mobile = models.PositiveIntegerField(default = 0)
    zipcode = models.PositiveIntegerField(default = 0)
    isDefault = models.BooleanField(default = False)

class SearchInfo(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    info = models.TextField(null=True)
    time = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # profile = Profile.objects.get(user = instance)
    # profile.save()
    if not instance.is_superuser:
        instance.profile.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=Address)
def create_address(sender,instance, **kwargs):
    qs = Address.objects.all()
    if qs.count() == 1 and instance.isDefault == False:
        instance.isDefault=True
        instance.save()


class Province(models.Model):
    idx = models.PositiveIntegerField(db_index=True, default=0)
    name = models.CharField(max_length=128,blank=True)

class City(models.Model):
    idx = models.PositiveIntegerField(db_index=True, default=0)
    name = models.CharField(max_length=128,blank=True)

class Distinct(models.Model):
    idx = models.PositiveIntegerField(db_index=True, default=0)
    name = models.CharField(max_length=128,blank=True)



