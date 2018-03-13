# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.dispatch
from django.dispatch import receiver
from rest_framework import status, generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from sku.models import Book, Banner, Category
from users.models import SearchInfo
from .serialize import JsonResponseSerializer, BooklistSerializer, CategorySerializer

userSearchSignal = django.dispatch.Signal(providing_args=["info","user"])





class libraryBookList(generics.ListAPIView):
    '''
    api used for wx index page to get book list
    '''


    queryset = Book.objects.all()
    serializer_class = BooklistSerializer

    #Auth and permission
    #authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    #permission_classes = (IsAuthenticated,)



    def get_queryset(self):
        queryset = Book.objects.all()
        category_id = self.request.query_params.get('cid', None)
        if category_id is not None:
            queryset = queryset.filter(cid__id = category_id)

        name = self.request.query_params.get('nameLike', None)
        if name.strip():
            print "user search " + name
            queryset = queryset.filter(name__contains=name)
            userSearchSignal.send(sender=self.__class__, info=name, user= self.request.user)

        return queryset


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        r = {
            "code" : 0,
            "msg"  : "OK",
            "data" : self.get_serializer(queryset,many=True).data
        }
        return Response(r)

class bookDetail(generics.RetrieveAPIView):
    '''
    api used for wx to get book detail information 
    '''
    queryset = Book.objects.all()
    serializer_class = BooklistSerializer
    lookup_field = 'isbn'
    

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        r = {
            "code" : 0,
            "msg"  : "OK",
            "data" : serializer.data
        }
        return Response(r)


# Create your views here.
@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
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
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
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
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
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


@receiver(userSearchSignal, sender=libraryBookList)
def userSearch_handle(sender, **kwargs):

    user = kwargs['user']
    if user == "AnonymousUser" :
        print "AnonymouseUser search"
        instance = SearchInfo.objects.create(info=kwargs['info'])
    else:
        print "login user search"
        instance = SearchInfo.objects.create(info=kwargs['info'], user=user.profile)

    instance.save()



class wxcategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


