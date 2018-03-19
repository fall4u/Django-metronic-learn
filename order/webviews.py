# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, renderers, status, generics
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from rest_framework.response import Response

from sku.models import LibBook
from sku.serialize import  LibbookSerializer
from .models import Order
from .serialize import OrderSerializer


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def webOrderPage(request):
    return render(request, 'p_orders.html')


class webOrderList(ListAPIView):
    '''
    used in weixin 
    return the qs according to the token
    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('createTime')
    ordering = ['-createTime', ]
    filter_fields = ('status',)


class webOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    # Get /Update /Delete a libbook
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'p_ordersDetail.html'

    def update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        print request.data
        instance = self.queryset.get(pk=pk)
        type = request.data['type']
        if type == "0":
            deliveryTime = request.data['deliveryTime']
            self._order_status_from_pay_to_deliver(pk , deliveryTime, None)

        if type == "1":
            libbooks = request.data.getlist('info')
            self._order_status_from_pay_to_deliver(pk , None, libbooks)

        if type == "2":
            self._order_status_from_delivery_to_confirm(pk)

        return HttpResponse(json.dumps({"status":"ok"}), content_type="application/json")

    def _order_status_from_delivery_to_confirm(self, pk):
        instance = self.queryset.get(pk=pk)
        if instance.status == Order.STATUS_TO_DELIVER :
            instance.status = Order.STATUS_TO_CONFIRM
            instance.save()

    def _order_status_from_pay_to_deliver(self, orderPk, deliveryTime, libbooks):
        instance = self.queryset.get(pk=orderPk)
        print (" _order_status_from_pay_to_deliver +++ ")
        if deliveryTime is not None:
            instance.deliveryTime = deliveryTime
            instance.status = Order.STATUS_TO_DELIVER #待发货
            instance.save()

        if libbooks is not None:
            for item in libbooks:
                libbook = LibBook.objects.get(pk=item)
                libbook.order = instance
                libbook.status = LibBook.STATUS_OUT #'4' #set status OUT
                libbook.save()
        else:
            print "libbooks is None"
        print (" _order_status_from_pay_to_deliver ---")

        return



class weborderStatistics(RetrieveAPIView):
    '''
    used in webadmin
    return the order statistics
    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        ret = {
            "count_id_no_pay": self.get_queryset().filter(status='0').count(),
            "count_id_no_transfer": self.get_queryset().filter(status='1').count(),
            "count_id_no_confirm": self.get_queryset().filter(status='2').count(),
           # "count_id_no_reputation": self.get_queryset().filter(status='3').count(),
            "count_id_success": self.get_queryset().filter(status=Order.STATUS_COMPLETED).count(),
            "count_id_pay": self.get_queryset().filter(status='6').count(),

        }
        return Response(ret, status=status.HTTP_200_OK)



@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def webOutbooksPage(request):
    return render(request, 'p_outbooks.html')


class webOutbooksList(ListAPIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    queryset = LibBook.objects.all()
    serializer_class = LibbookSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        objects = LibBook.objects.all()

        recordsTotal = objects.count()
        recordsFiltered = recordsTotal

        start = int(request.GET['start'])
        length = int(request.GET['length'])
        draw = int(request.GET['draw'])

        # filter objects according to user inputs
        serializer = LibbookSerializer(objects, many=True)

        objects = objects.filter(status = LibBook.STATUS_OUT)

        recordsFiltered = objects.count()

        objects = objects[start:(start + length)]

        serializer = LibbookSerializer(objects, many=True)
        # dic = [obj.as_dict() for obj in objects]

        print serializer.data

        resp = {
            'draw': draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsFiltered,
            'data': serializer.data,
        }

        return HttpResponse(json.dumps(resp), content_type="application/json")

