# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from sku.models import Book, Banner
from .serialize import JsonResponseSerializer


# Create your views here.
@api_view(['POST'])
def bannerDelete(request):
    isbn = request.POST['isbn']
    book = Book.objects.get_or_none(isbn=isbn)
    if book:
        banner = Banner.objects.get(book=book)
        if banner:
            serializer = JsonResponseSerializer({"code": 0, "msg": "OK", "data": []})
            r = JSONRenderer().render(serializer.data)
            # delete banner instance
            banner.delete()
            return Response(r)

    return Response({"code": 400, "msg": "fail", "data": []}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bannerMoveUp(request):
    isbn = request.POST['isbn']
    book = Book.objects.get_or_none(isbn=isbn)
    if book:
        banner = Banner.objects.get_or_none(book=book)
        if banner:
            banner.up()
            return Response({"code": 0, "msg": "OK", "data": []}, status=status.HTTP_200_OK)
        else:
            return Response({"code": 400, "msg": "banner not found", "data": []}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"code": 400, "msg": "fail", "data": []}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def bannerMoveDown(request):
    isbn = request.POST['isbn']
    book = Book.objects.get_or_none(isbn=isbn)
    if book:
        banner = Banner.objects.get_or_none(book=book)
        if banner:
            banner.down()
            return Response({"code": 0, "msg": "OK", "data": []}, status=status.HTTP_200_OK)
        else:
            return Response({"code": 400, "msg": "banner not found", "data": []}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"code": 400, "msg": "fail", "data": []}, status=status.HTTP_400_BAD_REQUEST)