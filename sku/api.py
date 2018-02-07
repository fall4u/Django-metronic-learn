# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from sku.models import Book, Banner, LibBook
from .serialize import JsonResponseSerializer, BooklistSerializer


class libraryBookList(generics.ListAPIView):
    '''
    api used for wx index page to get book list
    '''
    objects = LibBook.objects.all()
    booknames = objects.values_list("book__name")
    booklist = Book.objects.filter(name__in=booknames.distinct())
    queryset = booklist

    serializer_class = BooklistSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print "customize list"
        r = {
            "code" : 0,
            "msg"  : "OK",
            "data" : self.get_serializer(queryset,many=True).data
        }
        return Response(r)


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
