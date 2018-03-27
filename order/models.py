# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from model_utils import Choices

from sku.models import Book
from users.models import Profile
from .utils import unique_order_id_generator


# Create your models here.


class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects
    """

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class Order(models.Model):
    STATUS_ALL = ''
    STATUS_CREATE = '0'
    STATUS_TO_DELIVER = '1'
    STATUS_TO_CONFIRM = '2'
    STATUS_COMPLETED = '3'
    STATUS_USER_PAYED = '6'
    #
    # STATUS_CHOICES = (
    #     (STATUS_ALL, 'all'),
    #     (STATUS_USER_CREATE, 'create'),
    #     (STATUS_CANCEL, 'cancel'),
    #     (STATUS_NEED_HANDLE, 'handle'),
    #     (STATUS_IN_DELIVER, 'inDeliver'),
    #     (STATUS_TO_COMMENT, 'comment'),
    #     (STATUS_CLOSED, 'closed'),
    #     (STATUS_OVERDUE, 'overdue'),
    # )

    STATUS = Choices(
        ('', 'All'),
        ('0', u'待支付'),
        ('1', u'待发货'),
        ('2', u'待收货'),
        ('3', u'已完成'),
        # ('4', u'已完成'),
        # ('5', u'已超期'),
        ('6', u'已付款'),
    )
    goods = models.ManyToManyField(Book, through='OrderGoodsDetail')
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)

    remark = models.TextField(null=True, default='', blank=True)
    orderId = models.CharField(max_length=32, blank=True)

    status = models.CharField(max_length=1, choices=STATUS, default='0')
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
    deliveryTime = models.DateTimeField(null=True, blank=True)
    dueDate = models.DateField(blank=True, null=True)

    goodsFee    = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)
    deliveryFee = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)
    serviceFee  = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)

    objects = GetOrNoneManager()

    def __unicode__(self):
        return "%s %s %s" %(self.user.nickName , self.createTime.strftime('%Y-%m-%d'), self.status)

class OrderGoodsDetail(models.Model):
    sku = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)


@receiver(pre_save, sender=Order)
def pre_save_create(sender, instance, *args, **kwargs):
    # create order id
    if not instance.orderId:
        instance.orderId = unique_order_id_generator(instance)
    # create total charge fee
    instance.goodsFee = 0
    instance.deliveryFee = 0
    instance.serviceFee = 4.8


# @receiver(post_save, sender=Order)
# def order_add_goods(sender,instance, **kwargs):
#     pass
