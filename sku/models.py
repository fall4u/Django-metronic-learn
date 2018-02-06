# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.db.models import Max


# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects
    """

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class Book(models.Model):
    name = models.CharField(max_length=48)
    isbn = models.IntegerField(primary_key=True, unique=True)
    author = models.CharField(max_length=24)
    press = models.CharField(max_length=48)
    price = models.PositiveIntegerField(default=0)
    outAmount = models.PositiveIntegerField(default=0)
    totalOutAmount = models.PositiveIntegerField(default=0)
    totalBrokenAmount = models.PositiveIntegerField(default=0)
    cover = models.ImageField(default="lpic/default_cover.jpg")
    objects = GetOrNoneManager()


    def __unicode__(self):
        return "%s %d" % (self.name, self.isbn)

class LibBook(models.Model):
    STATUS_ALL = ''
    STATUS_ONLINE = '1'
    STATUS_OFFLINE = '2'
    STATUS_IDLE = '3'
    STATUS_OUT = '4'
    STATUS_BOOKED = '5'
    STATUS_BROKEN = '6'
    STATUS_DUEDATE = '7'
    STATUS_CHOICES = (
        (STATUS_ALL, 'all'),
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


        # def __unicode__(self):
        #     return "%s %s %s" %(self.book.name , self.inDate.strftime('%Y-%m-%d'), str(self.uuid))


class Banner(models.Model):
    # Relations
    s = models.PositiveIntegerField(editable=False, db_index=True)
    book = models.OneToOneField(Book, on_delete=models.PROTECT, null=False)
    clickCount = models.PositiveIntegerField(default=0)

    objects = GetOrNoneManager()

    class Meta:
        ordering = ('s',)

    def _swap_qs0(self, qs):
        """
        Swap the positions of this object with first result, if any, from the provided queryset.
        """
        try:
            replacement = qs[0]
            print "_swap_qs"
            print replacement.book.name
            print replacement.s

            print replacement
        except IndexError:
            # already first/last
            return
        self.swap(replacement)

    def swap(self, replacement):
        """
        Swap the position of this object with a replacement object.
        """

        order, replacement_order = getattr(self, 's'), getattr(replacement, 's')
        print order, replacement_order
        setattr(self, 's', replacement_order)
        setattr(replacement, 's', order)
        self.save()
        replacement.save()

    def down(self):
        self._swap_qs0(Banner.objects.all().filter(**{'s' + '__gt': getattr(self, 's')}))

    def up(self):
        self._swap_qs0(Banner.objects.all().filter(**{'s' + '__lt': getattr(self, 's')}))

    def save(self, *args, **kwargs):
        if getattr(self, 's') is None:
            qs = Banner.objects.all()
            dic = qs.aggregate(Max('s'))
            c = dic.get('s__max')
            if c is None:
                setattr(self, 's', 0)
            else:
                setattr(self, 's', c + 1)
        super(Banner, self).save(*args, **kwargs)
