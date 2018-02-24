# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from sku.models import Book
from uploadimages.models import UploadedImage
from uploadimages.serialize import UploadedImageSerializer
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


#
# class BooklistSerializer(DynamicFieldsModelSerializer):
#     totalAmount = serializers.SerializerMethodField(read_only=True)
#     isbn = serializers.IntegerField(required=False)
#     pics = serializers.SerializerMethodField()
#     stores = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Book
#         fields = ('pics', 'name', 'isbn', 'author', 'press', 'price', 'totalAmount', 'outAmount', 'totalOutAmount',
#                   'totalBrokenAmount', 'desc', 'stores')
#
#     def get_totalAmount(self, obj):
#         return obj.libbook_set.count()
#
#     def get_pics(self, obj):
#         qs = UploadedImage.objects.all()
#         qs = qs.filter(isbn=obj.isbn)
#
#         serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
#         return serialize.data
#
#     def get_stores(self,obj):
#         return self.get_totalAmount(obj) - obj.outAmount
#
#
#
#
# class BannerSerializer(serializers.ModelSerializer):
#     book = BooklistSerializer(required=True, fields={'name', 'isbn', 'author', 'press', 'price'})
#     pics = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Banner
#         fields = ('book', 'pics')
#
#     def get_pics(self, obj):
#         qs = UploadedImage.objects.all()
#         qs = qs.filter(isbn=obj.book.isbn)
#
#         serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
#         return serialize.data


class OrderGoodsDetailSerializer(DynamicFieldsModelSerializer):
    isbn = serializers.ReadOnlyField(source='sku.isbn')
    name = serializers.ReadOnlyField(source='sku.name')
    price = serializers.ReadOnlyField(source='sku.price')

    pics = serializers.SerializerMethodField()

    class Meta:
        model = OrderGoodsDetail
        fields = ('isbn', 'name', 'price', 'amount', 'pics')

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

    status = ChoicesField(required=False, choices=Order.STATUS)
    stsidx = serializers.SerializerMethodField()
    totalCharge = serializers.SerializerMethodField()
    createTime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    updateTime = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Order
        fields = (
        'stsidx', 'goods', 'status', 'pk', 'remark', 'createTime', 'updateTime', 'orderId', 'totalCharge', 'goodsFee',
        'deliveryFee', 'serviceFee')

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
