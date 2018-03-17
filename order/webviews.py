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

        return HttpResponse(json.dumps({"status":"ok"}), content_type="application/json")

    def _order_status_from_pay_to_deliver(self, orderPk, deliveryTime, libbooks):
        instance = self.queryset.get(pk=orderPk)

        if deliveryTime is not None:
            instance.deliveryTime = deliveryTime
            instance.status = Order.STATUS_TO_DELIVER #待发货
            instance.save()

        if libbooks is not None:
            for item in libbooks:
                libbook = LibBook.objects.get(pk=item)
                libbook.order = instance
                libbook.status = '4' #set status OUT
                libbook.save()





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
            "count_id_no_reputation": self.get_queryset().filter(status='3').count(),
            "count_id_success": self.get_queryset().filter(status='4').count(),
            "count_id_pay": self.get_queryset().filter(status='6').count(),

        }
        return Response(ret, status=status.HTTP_200_OK)
