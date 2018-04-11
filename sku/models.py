# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.db.models import Max

from users.models import Profile


# from order.models import Order


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


class Category(models.Model):
    name = models.CharField(max_length=48)
    objects = GetOrNoneManager()

    # ording
    s = models.PositiveIntegerField(editable=False, db_index=True)

    class Meta:
        ordering = ('s',)

    def _swap_qs0(self, qs):
        """
        Swap the positions of this object with first result, if any, from the provided queryset.
        """
        try:
            replacement = qs[0]
            print "_swap_qs"

        except IndexError:
            # already first/last
            return
        self.swap(replacement)

    def swap(self, replacement):
        """
        Swap the position of this object with a replacement object.
        """

        order, replacement_order = getattr(self, 's'), getattr(replacement, 's')
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
            qs = Category.objects.all()
            dic = qs.aggregate(Max('s'))
            c = dic.get('s__max')
            if c is None:
                setattr(self, 's', 0)
            else:
                setattr(self, 's', c + 1)
        super(Category, self).save(*args, **kwargs)


class Book(models.Model):
    name = models.CharField(max_length=128)
    isbn = models.IntegerField(primary_key=True, unique=True)
    author = models.CharField(max_length=128)
    press = models.CharField(max_length=128)
    price = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)
    outAmount = models.PositiveIntegerField(default=0)
    totalOutAmount = models.PositiveIntegerField(default=0)
    totalBrokenAmount = models.PositiveIntegerField(default=0)
    desc = models.TextField(null=True)

    # Relations
    cid = models.ManyToManyField(Category)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return "%s %d" % (self.name, self.isbn)


class LibBook(models.Model):
    STATUS_ALL = ''
    STATUS_ONLINE = '1'
    STATUS_OFFLINE = '2'
    STATUS_OUT = '4'
    STATUS_BOOKED = '5'
    STATUS_BROKEN = '6'
    STATUS_DUEDATE = '7'
    STATUS_CHOICES = (
        (STATUS_ALL, 'all'),
        (STATUS_ONLINE, 'online'),
        (STATUS_OFFLINE, 'offline'),
        (STATUS_OUT, 'out'),
        (STATUS_BOOKED, 'booked'),
        (STATUS_BROKEN, 'broken'),
        (STATUS_DUEDATE, 'overdue'),
    )
    # Relations
    book = models.ForeignKey(Book, on_delete=models.PROTECT, null=False)
    from order.models import Order
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    # Attributes
    # 3F2504E0-4F89-11D3-9A0C-0305E82C3301

    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    inDate = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_OFFLINE, max_length=2)
    dueDate = models.DateField(blank=True, null=True)
    overDays = models.PositiveIntegerField(default=0)
    LendAmount = models.PositiveIntegerField(default=0)
    isReal = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return "%s %s %s isReal: %d" % (self.book.name, self.inDate.strftime('%Y-%m-%d'), str(self.uuid), self.isReal)

    @classmethod
    def acquire_books(cls, books):
        ret = 0
        for item in books:
            amount = item['amount']
            if amount > cls.objects.select_for_update().filter(book__isbn=item['isbn']).filter(
                    status=LibBook.STATUS_ONLINE).count():
                return ret

        for item in books:
            amount = item['amount']
            for i in range(amount):
                instance = cls.objects.select_for_update().filter(book__isbn=item['isbn']).filter(
                    status=LibBook.STATUS_ONLINE).first()
                if instance:
                    instance.status = LibBook.STATUS_OFFLINE
                    instance.save()
        ret = 1

        return ret

    @classmethod
    def release_books(cls, books):
        print "+++ release books +++"
        ret = 0
        for item in books:
            isbn = item.sku.isbn
            if item.amount > cls.objects.select_for_update().filter(book__isbn=isbn).filter(
                    status=LibBook.STATUS_OFFLINE).count():
                print "error: this could not happen"
                return ret

        for item in books:
            amount = item.amount
            isbn = item.sku.isbn
            for i in range(amount):
                instance = cls.objects.select_for_update().filter(book__isbn=isbn).filter(
                    status=LibBook.STATUS_OFFLINE).first()
                if instance:
                    instance.status = LibBook.STATUS_ONLINE
                    instance.save()
        ret = 1
        print "--- release books ---"
        return


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

        except IndexError:
            # already first/last
            return
        self.swap(replacement)

    def swap(self, replacement):
        """
        Swap the position of this object with a replacement object.
        """

        order, replacement_order = getattr(self, 's'), getattr(replacement, 's')
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


class Coupon(models.Model):
    STATUS_ALL= ''
    STATUS_UNUSE = '1'
    STATUS_USED = '2'
    STATUS_S = (
        (STATUS_ALL, 'all'),
        (STATUS_UNUSE, 'unuse'),
        (STATUS_USED, 'used'),
    )

    objects = GetOrNoneManager()

    name      = models.CharField(max_length=128)
    startTime = models.DateField(null=True)
    endTime   = models.DateField(null=True)
    usedTime  = models.DateField(null=True)
    status    = models.CharField(choices=STATUS_S, default=STATUS_UNUSE, max_length=2)
    amount    = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)
    uuid      = models.UUIDField(default=uuid.uuid4, null=False)
    createTime = models.DateTimeField(auto_now_add=True)

    # Relations
    users =  models.ForeignKey(Profile, on_delete=models.CASCADE)