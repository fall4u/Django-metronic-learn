# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class Book(models.Model):
    name = models.CharField(max_length=48)
    isbn = models.IntegerField(primary_key = True)
    author = models.CharField(max_length=24)
    press = models.CharField(max_length=48)
    price = models.PositiveIntegerField(default=0)
    totalAmount = models.PositiveIntegerField(default=0)
    outAmount = models.PositiveIntegerField(default=0)
    totalOutAmount = models.PositiveIntegerField(default=0)
    totalBrokenAmount = models.PositiveIntegerField(default=0)

    # def __init__(self, name, author, press, price, isbn):
    #     self.name = name
    #     self.author = author
    #     self.press = press
    #     self.price = price
    #     self.isbn = isbn
    #     self.totalAmount = 0
    #     self.outAmount = 0
    #     self.totalOutAmount = 0
    #     self.totalBrokenAmount = 0
        
    @property
    def as_dict(self):
    	return dict(name=self.name, isbn=self.isbn, author=self.author, press=self.press, price=self.price,
                    totalAmount=self.totalAmount, outAmount=self.outAmount, totalOutAmount=self.totalOutAmount,
                    totalBrokenAmount=self.totalBrokenAmount)
