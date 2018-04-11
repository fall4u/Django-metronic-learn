# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

import django.dispatch
from django.dispatch import receiver
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from sku.models import Book, Banner, Category, Coupon
from users.models import SearchInfo
from .serialize import JsonResponseSerializer, BooklistSerializer, CategorySerializer, CouponSerializer
from .tools import create_discount

userSearchSignal = django.dispatch.Signal(providing_args=["info","user"])



class getCoupon(generics.CreateAPIView):
    '''
    api used for wx user to get coupon after share to others
        coupon amount is random 
    '''

    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    # Auth and permission
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        qs = Coupon.objects.filter(users=request.user.profile).filter(startTime = date.today())
        if qs.count() == 0:
            discount = create_discount(1,48)
            instance = Coupon.objects.create(name = "shareCoupon", users= request.user.profile, startTime = date.today() , endTime = date.today(), amount = discount )
        else:
            print "this user already get coupon today"
            return Response({"detail": "already get today"}, status = status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)


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



class listCoupon(generics.ListAPIView):
    '''
    api used for wx index page to get book list
    '''


    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)

    #Auth and permission
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    ordering_fields = ('createTime')
    ordering = ['-createTime', ]

    def get_queryset(self):
        qs = self.queryset.filter(users=self.request.user.profile)
        return qs



    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        r = {
            "code" : 0,
            "msg"  : "OK",
            "data" : self.get_serializer(queryset,many=True).data
        }
        return Response(r)
