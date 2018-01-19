# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
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

    @property
    def as_dict(self):
        return dict(name=self.name, isbn=self.isbn, author=self.author, press=self.press, price=self.price,
                    totalAmount=self.totalAmount, outAmount=self.outAmount, totalOutAmount=self.totalOutAmount,
                    totalBrokenAmount=self.totalBrokenAmount)

        # def __unicode__(self):
        #     return "%s %d" %(self.name , self.isbn)

class LibBook(models.Model):
    STATUS_ONLINE = '1'
    STATUS_OFFLINE = '2'
    STATUS_IDLE = '3'
    STATUS_OUT = '4'
    STATUS_BOOKED = '5'
    STATUS_BROKEN = '6'
    STATUS_DUEDATE = '7'
    STATUS_CHOICES = (
        (STATUS_ONLINE, 'online'),
        (STATUS_OFFLINE, 'offline'),
        (STATUS_IDLE, 'idle'),
        (STATUS_OUT, 'out'),
        (STATUS_BOOKED, 'booked'),
        (STATUS_BROKEN, 'broken'),
        (STATUS_DUEDATE, 'overdue'),
    )
    # Relations
    book = models.ForeignKey(Book, on_delete=models.PROTECT,null=False)
    # Attributes
    # 3F2504E0-4F89-11D3-9A0C-0305E82C3301

    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    inDate = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_OFFLINE, max_length=2)
    dueDate = models.DateField(blank=True, null=True)
    overDays = models.PositiveIntegerField(default=0)
    LendAmount = models.PositiveIntegerField(default=0)

    def as_dict(self):
        u=dueD=inD = ''
        if isinstance(self.uuid, uuid.UUID):
            u = str(self.uuid)
        if isinstance(self.inDate, datetime.date):
            inD = self.inDate.strftime('%Y-%m-%d')
        if isinstance(self.dueDate, datetime.date):
            dueD = self.dueDate.strftime('%Y-%m-%d')  


        return dict(uid=u, name =self.book.name, isbn=self.book.isbn, author = self.book.author, press = self.book.press,
                    price=self.book.price, inDate=inD, Status=self.get_status_display(), Due=dueD,
                    OverDate=self.overDays, Counts = self.LendAmount)

        # def __unicode__(self):
        #     return "%s %s %s" %(self.book.name , self.inDate.strftime('%Y-%m-%d'), str(self.uuid))
