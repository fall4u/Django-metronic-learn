# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Book, Banner, LibBook


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('name', 'isbn', 'author', 'press', 'price')


class BooklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
        'name', 'isbn', 'author', 'press', 'price', 'totalAmount', 'outAmount', 'totalOutAmount', 'totalBrokenAmount',
        'cover')

class BannerSerializer(serializers.ModelSerializer):
    book = BookSerializer(required=True)

    class Meta:
        model = Banner
        fields = ('book',)


class LibbookSerializer(serializers.ModelSerializer):
    book = BookSerializer(required=True)
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = LibBook
        fields = ('uuid', 'book', 'inDate', 'status', 'dueDate', 'overDays', 'LendAmount')


class JsonResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    msg = serializers.CharField()
    data = serializers.JSONField(required=False)
