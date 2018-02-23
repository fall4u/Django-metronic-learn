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



class Order(models.Model):
    # STATUS_ALL = ''
    # STATUS_USER_CREATE = '1' #订单创建  （已经下单，未付款，用户可以取消和付款） 对应小程序 待付款
    # STATUS_NEED_HANDLE = '3' #订单待处理 （用户已经付款， 等待后台处理）       对应小程序  待发货
    # STATUS_IN_DELIVER  = '4' #已发货 待确认                                对应小程序  待收货
    # STATUS_TO_COMMENT  = '5' #已收货 待评价                                对应小程序  待评价
    # STATUS_CLOSED      = '6' #已经评价
    # STATUS_OVERDUE     = '7'
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
        ('3', u'待评价'),
        ('4', u'已完成'),
        ('5', u'已超期'),
    )
    goods = models.ManyToManyField(Book, through='OrderGoodsDetail')
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)

    remark = models.TextField(null=True, default='', blank=True)
    orderId = models.CharField(max_length=32, blank=True)

    status = models.CharField(max_length=1, choices=STATUS, default='0')
    createTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)
    dueDate = models.DateField(blank=True, null=True)

    totalCharge = models.DecimalField(default=0.00, max_digits=6, decimal_places=2)


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
    instance.totalCharge = get_totalCharge(instance)


def get_totalCharge(instance):
    goodsFee = 0
    deliveryFee = 0
    serviceFee = 4.8
    return goodsFee + deliveryFee + serviceFee

# @receiver(post_save, sender=Order)
# def order_add_goods(sender,instance, **kwargs):
#     pass
