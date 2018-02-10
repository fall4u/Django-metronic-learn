# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Book, Banner, LibBook


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



class BooklistSerializer(DynamicFieldsModelSerializer):
    totalAmount = serializers.SerializerMethodField(read_only=True)
    isbn = serializers.IntegerField(required=False)

    class Meta:
        model = Book
        fields = ('name', 'isbn', 'author', 'press', 'price', 'totalAmount', 'outAmount', 'totalOutAmount', 'totalBrokenAmount','cover','desc')

    def get_totalAmount(self, obj):
        return obj.libbook_set.count()

    # def to_representation(self,obj):
    # 	return "book(%d, %s,%s, %f)"%(obj.isbn, obj.name,obj.author,obj.price/100)

class BannerSerializer(serializers.ModelSerializer):
    book = BooklistSerializer(required=True,fields={'name','isbn','author','press','price','cover'})

    class Meta:
        model = Banner
        fields = ('book',)


class LibbookSerializer(serializers.ModelSerializer):
    book = BooklistSerializer(required=False,fields={'name','isbn','author','press','price','cover'})

    class Meta:
        model = LibBook
        fields = ('uuid', 'book', 'inDate', 'status', 'dueDate', 'overDays', 'LendAmount')


class JsonResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    msg = serializers.CharField()
    data = serializers.JSONField(required=False)
