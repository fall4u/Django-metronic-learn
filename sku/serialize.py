# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Book, Banner


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('name', 'isbn', 'author')


class BannerSerializer(serializers.ModelSerializer):
    book = BookSerializer(required=True)

    class Meta:
        model = Banner
        fields = ('book',)


class JsonResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    msg = serializers.CharField()
    data = serializers.JSONField(required=False)
