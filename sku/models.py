# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class Book(models.Model):
    name = models.CharField(max_length=48)
    author = models.CharField(max_length=24)
    isbn = models.IntegerField()
    status = models.CharField(max_length=12)
    press = models.CharField(max_length=48)
    acount = models.IntegerField()
    lendCount = models.IntegerField()

    def as_dict(self):
    	return {
    		"name": self.name,
    		"author": self.author,
    		"isbn" : self.isbn,
    		"status" : self.status,
    		"press" : self.press,
    		"acount" : self.acount,
    		"lendCount" : self.lendCount
    	}
