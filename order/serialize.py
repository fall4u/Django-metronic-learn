# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from sku.models import Book
from uploadimages.models import UploadedImage
from uploadimages.serialize import UploadedImageSerializer
from users.models import Address
from users.serialize import AddressSerializer
from users.serialize import UserProfileSerializer
from .models import Order, OrderGoodsDetail


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class OrderGoodsDetailSerializer(DynamicFieldsModelSerializer):
    isbn = serializers.ReadOnlyField(source='sku.isbn')
    name = serializers.ReadOnlyField(source='sku.name')
    price = serializers.ReadOnlyField(source='sku.price')

    pics = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    inStock = serializers.SerializerMethodField()

    class Meta:
        model = OrderGoodsDetail
        fields = ('isbn', 'name', 'price', 'amount', 'pics', 'available', 'inStock')

    def to_internal_value(self, data):
        ret = {
            "isbn": data['isbn'],
            "name": data['name'],
            "amount": data['amount'],
        }
        return ret

    def get_pics(self, obj):
        qs = UploadedImage.objects.all()
        qs = qs.filter(isbn=obj.sku.isbn)

        serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
        return serialize.data

    #获得可用库存数量
    def get_available(self, obj):
        avail = obj.sku.libbook_set.filter(status="1").count()
        print "avail = %d"%(avail)
        return avail
    #获得实际库存数量
    def get_inStock(self, obj):
        store = obj.sku.libbook_set.count()
        print obj.sku.libbook_set
        print obj.sku
        print "--- get_inStock ---"
        return store

class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        return getattr(self._choices, data)


class OrderSerializer(DynamicFieldsModelSerializer):
    goods = OrderGoodsDetailSerializer(source='ordergoodsdetail_set', many=True)
    user = UserProfileSerializer(read_only=True)
    status = ChoicesField(required=False, choices=Order.STATUS)
    stsidx = serializers.SerializerMethodField()
    addr = serializers.SerializerMethodField()
    totalCharge = serializers.SerializerMethodField()
    createTime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updateTime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Order
        fields = (
        'stsidx', 'goods', 'status', 'pk', 'remark', 'createTime', 'updateTime', 'orderId', 'totalCharge', 'goodsFee',
        'deliveryFee', 'serviceFee','user', 'addr')

    def create(self, validated_data):
        status = '0'
        print  validated_data
        remark = validated_data.pop('remark')
        user = validated_data.pop('user')
        goods = validated_data.pop('ordergoodsdetail_set')
        instance = Order.objects.create(status=status, remark=remark, user=user)
        for good in goods:
            sku = Book.objects.get(isbn=good['isbn'])
            OrderGoodsDetail.objects.create(order=instance, sku=sku, amount=good['amount'])
        return instance

    def get_stsidx(self, obj):
        return obj.status

    def get_totalCharge(self, obj):
        return obj.goodsFee + obj.deliveryFee + obj.serviceFee

    def get_addr(self, obj):
        #user = Profile.objects.filter(user = self.user)
        addrs = Address.objects.filter(user=obj.user)
        addr = addrs.get(isDefault=True)

        return AddressSerializer(addr).data