# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models


# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class Book(models.Model):
    name = models.CharField(max_length=48)
    isbn = models.IntegerField(primary_key=True, unique=True)
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

    def __unicode__(self):
        return "%s %d" %(self.name , self.isbn)

class LibBook(models.Model):
    STATUS_ONLINE = 1
    STATUS_OFFLINE = 2
    STATUS_IDLE = 3
    STATUS_OUT = 4
    STATUS_BOOKED = 5
    STATUS_BROKEN = 6
    STATUS_DUEDATE = 7
    STATUS_CHOICES = {
        (STATUS_ONLINE, 'online'),
        (STATUS_OFFLINE, 'offline'),
        (STATUS_IDLE, 'idle'),
        (STATUS_OUT, 'out'),
        (STATUS_BOOKED, 'booked'),
        (STATUS_BROKEN, 'broken'),
        (STATUS_DUEDATE, 'overdue'),
    }
    # 3F2504E0-4F89-11D3-9A0C-0305E82C3301

    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    book = models.ForeignKey(Book, on_delete=models.PROTECT,null=True)
    inDate = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_OFFLINE, max_length=2)
    dueDate = models.DateField(blank=True, null=True)
    overDays = models.PositiveIntegerField(default=0)
    LendAmount = models.PositiveIntegerField(default=0)

    @property
    def as_dict(self):
        return dict(uid=self.uuid, isbn=self.isbn, inDate=self.inDate, status=self.status, dueDate=self.dueDate,
                    overDays=self.overDays, LendAmount=self.LendAmount)

    def __unicode__(self):
        return "%s %s %s" %(self.book.name , self.inDate, self.uuid)