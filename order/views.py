# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serialize import OrderSerializer


# Create your views here.


class order(RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    # api for wx users create a order
    def put(self, request, *args, **kwargs):
        print "+++ order create +++"
        print request.data

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print "valid"
            serializer.save(user=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.data.get('pk', ''))


class orderList(ListAPIView):
    '''
    used in weixin 
    return the qs according to the token
    '''

    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('createTime')
    ordering = ['-createTime', ]
    filter_fields = ('status',)

    # def list(self, request, *args, **kwargs):
    # 	status = request.GET.get('status', '')
    #     print status
    #     if status:
    #         qs = self.get_queryset().filter(user=request.user.profile)
    #         print qs
    #         print qs.count()
    #         print status
    #         qs = qs.filter(status=status)
    #         print qs
    #         print qs.count()
    #         serialize = self.get_serializer(qs, many=True)
    #         return Response(serialize.data)
    #     return Response("fail", status=status.HTTP_400_BAD_REQUEST)
    def get_queryset(self):
        qs = self.queryset.filter(user=self.request.user.profile)
        return qs


class orderFee(RetrieveAPIView):
    '''
    used in weixin
    return the order total charge including goodsFee/deliveryFee/serviceFee
    '''

    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        ret = {
            "serviceFee": 4.8,
            "allGoodsPrice": 0,
            "deliveryFee": 0,
        }
        return Response(ret, status=status.HTTP_200_OK)


class orderStatistics(RetrieveAPIView):
    '''
    used in weixin
    return the order statistics
    '''
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.profile
        return self.queryset.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        ret = {
            "count_id_no_pay": self.get_queryset().filter(status='0').count(),
            "count_id_no_transfer": self.get_queryset().filter(status='1').count(),
            "count_id_no_confirm": self.get_queryset().filter(status='2').count(),
            "count_id_no_reputation": self.get_queryset().filter(status='3').count(),
            "count_id_success": self.get_queryset().filter(status='4').count(),
        }
        return Response(ret, status=status.HTTP_200_OK)
