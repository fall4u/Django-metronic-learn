# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from uploadimages.models import UploadedImage
from uploadimages.serialize import UploadedImageSerializer
from .models import Book, Banner, LibBook, Category


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


class ManyToManyField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, obj):
        categorys = []
        details = {}
        details['id'] = obj.id
        details['name'] = obj.name
        categorys.append(details)

        return  details




class BooklistSerializer(DynamicFieldsModelSerializer):
    totalAmount = serializers.SerializerMethodField(read_only=True)
    isbn = serializers.IntegerField(required=False)
    pics = serializers.SerializerMethodField()
    stores = serializers.SerializerMethodField()

    #cid = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    cid = ManyToManyField(many=True, queryset=Category.objects.all())

    class Meta:
        model = Book
        fields = ('pics', 'name', 'isbn', 'author', 'press', 'price', 'totalAmount', 'outAmount', 'totalOutAmount',
                  'totalBrokenAmount', 'desc', 'stores', 'cid')

    def get_totalAmount(self, obj):
        store = obj.libbook_set.count()
        if store < 3:
            store = 3
        return store

    def get_pics(self, obj):
        qs = UploadedImage.objects.all()
        qs = qs.filter(isbn=obj.isbn)

        serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
        return serialize.data

    def get_stores(self, obj):
        outbooks = obj.libbook_set.filter(status=LibBook.STATUS_OUT).count()
        return self.get_totalAmount(obj) - outbooks




class BannerSerializer(serializers.ModelSerializer):
    book = BooklistSerializer(required=True, fields={'name', 'isbn', 'author', 'press', 'price'})
    pics = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ('book', 'pics')

    def get_pics(self, obj):
        qs = UploadedImage.objects.all()
        qs = qs.filter(isbn=obj.book.isbn)

        serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
        return serialize.data


class LibbookSerializer(serializers.ModelSerializer):
    book = BooklistSerializer(required=False, fields={'name', 'isbn', 'author', 'press', 'price'})
    pics = serializers.SerializerMethodField()
#    order = OrderSerializer(required=False)
    order = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = LibBook
        fields = ('uuid', 'book', 'inDate', 'status', 'dueDate', 'overDays', 'LendAmount', 'pics', 'pk', 'order',
                  'user','isReal')

    def get_pics(self, obj):
        qs = UploadedImage.objects.all()
        qs = qs.filter(isbn=obj.book.isbn)

        serialize = UploadedImageSerializer(qs, fields={'image'}, many=True)
        return serialize.data

    def get_order(self, obj):
        ret = None
        if obj.order:
            ret = obj.order.pk
        return ret

    def get_user(self,obj):
        ret = None
        if obj.order:
            ret = obj.order.user.nickName

        return ret

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('pk', 'name')

class JsonResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    msg = serializers.CharField()
    data = serializers.JSONField(required=False)

