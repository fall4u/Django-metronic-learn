from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction

from sku.models import LibBook
from .models import Order


@shared_task
def cancel_order(orderId):
    print('celery cancel orderId')
    print orderId
    instance = Order.objects.get_or_none(pk=orderId)
    print instance
    if instance and instance.status == Order.STATUS_CREATE:
        with transaction.atomic():
            LibBook.release_books(instance.ordergoodsdetail_set.all())
        instance.delete()
        print "instance delete"
    else:
        print "instance not cancel"

    return


@shared_task
def send_new_order_payed_mail():
    send_mail(
        'New Order',
        'please handle it',
        'peter.zhu@koolpos.com',
        ['fall4u@qq.com'],
        fail_silently=False, )
