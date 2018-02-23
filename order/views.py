# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
# Create your views here.
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serialize import OrderSerializer


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


class orderList(ListAPIView):
    '''
    used in weixin 
    return the qs according to the token
    '''

    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
    	status = request.GET.get('status', '')
        print status
        if status:
            qs = self.get_queryset().filter(user=request.user.profile)
            print qs
            print qs.count()
            print status
            qs = qs.filter(status=status)
            print qs
            print qs.count()
            serialize = self.get_serializer(qs, many=True)
            return Response(serialize.data)
        return Response("fail", status=status.HTTP_400_BAD_REQUEST)

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
        return Response(ret)


