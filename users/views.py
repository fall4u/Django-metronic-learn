# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import time
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import renderers, status, filters
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from order.models import Order
# Create your views here.
from .cons import Constant
from .form_user_login import UserForm
from .models import Profile, Address, SearchInfo, RequestBookInfo
from .serialize import UserProfileSerializer, AddressSerializer, SearchInfoSerializer, RequestBookInfoSerializer
from .wxapp import WXAppData


class loginView(generic.View):
    form_class = UserForm

    def get(self, request):
        return render(request,"page_user_login_1.html")

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            print "form is valid"
            print form.cleaned_data
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username = user, password = password)

            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                raise Http404("User is not invalid")
        else:
            print form.errors
#            return HttpResponse("form is not valid")

#def login(request):
#    return render(request, "page_user_login_1.html")
@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def index(request):
    return render(request, "index.html")


@api_view(['POST'])
def wxlogin(request):
    code = request.POST.get('code','').strip()

    encrypt_data = request.POST.get('encrypt_data')
    iv = request.POST.get('iv')
    print "encrypt_data = %s"%encrypt_data
    print "code = %s"%code
    print "iv = %s"%iv

    wxapp_data = WXAppData(appId = Constant.APPID , secret= Constant.APPSECRET)
    token = wxapp_data.get_token(code=code, encrypt_data=encrypt_data,iv=iv)

    result = {
        'code':0,
        'token': token.key
    }
    return Response(result)


class UserList(ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer

    authentication_classes = (TokenAuthentication,BasicAuthentication,SessionAuthentication)
    permission_class = (IsAuthenticated,)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print serializer.data
        return Response(serializer.data)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def notice(request):
    return render(request, 'p_notice.html')


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def User(request):
    return render(request, 'p_users.html')

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def searchInfo(request):
    return render(request, 'p_usersearchinfo.html')


class searchInfoList(ListAPIView):
    queryset = SearchInfo.objects.all()
    serializer_class = SearchInfoSerializer

    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    permission_class = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print serializer.data
        return Response(serializer.data)




class getDefaultAddress(RetrieveAPIView):
    authentication_classes = (TokenAuthentication,BasicAuthentication,SessionAuthentication)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(user = request.user.profile)
        obj = get_object_or_404(qs, isDefault = True)
        serialize = self.get_serializer(obj)
        return Response(serialize.data)


class wxaddressList(ListAPIView):
    authentication_classes = (TokenAuthentication,BasicAuthentication,SessionAuthentication)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(user=request.user.profile)
        serialize = self.get_serializer(qs, many=True)
        return Response(serialize.data)


class webaddressList(ListAPIView):
    '''
    used in admin web interface
    return the qs according to the user pk 
    '''
    authentication_classes = (TokenAuthentication,BasicAuthentication,SessionAuthentication)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)


    def list(self, request, *args, **kwargs):
        pk = kwargs.pop('pk')
        profile = Profile.objects.get(pk=pk)
        queryset = self.get_queryset().filter(user=profile)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class address(RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,BasicAuthentication,SessionAuthentication)
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    #api for wx users create a new address
    def put(self, request, *args, **kwargs):
        print "+++ address put +++"
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print "valid"
            serializer.save(user=request.user.profile)
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        print " +++ retrieve +++"
        pk = request.GET.get('pk','')
        if pk is not None:
            addr = Address.objects.get(pk=pk)
            serialize = self.get_serializer(addr)
            print serialize.data
            return Response(serialize.data, status = status.HTTP_200_OK)

        return Response("fail", status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user 
        return Address.objects.filter(user=user.profile)


    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.request.data.get('pk',''))

    def partial_update(self,request, *args, **kwargs):
        print request.data 
        #change the current default address's default flag
        flag = request.data.get('isDefault','')
        if flag:
            o = get_object_or_404(self.get_queryset(), isDefault=True)
            o.isDefault = False
            o.save()

        #handle the edit one 
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self,request,*args, **kwargs):
        qs = self.get_queryset()
        old = get_object_or_404(qs, isDefault=True)

        if qs.count() != 1 and old.pk == self.request.data.get('pk',''):
            qs = qs.exclude(isDefault=True)
            newo = qs[0]
            newo.isDefault=True
            newo.save()   

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)




class profile(RetrieveUpdateDestroyAPIView):
    # Get /Update /Delete a libbook
    queryset = Profile.objects.all()
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'p_userdetail.html'
    serializer_class = UserProfileSerializer

    # def retrieve(self, request, *args, **kwargs):
    #     uuid = kwargs.pop('uuid')
    #     libbook = get_object_or_404(LibBook, uuid=uuid)
    #     serializer = UserProfileSerializer(libbook)
    #     return Response({'profile': serializer.data})




class Statistics(RetrieveAPIView):
    '''
    used in webadmin
    return the order statistics
    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'index.html'

    def retrieve(self, request, *args, **kwargs):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        print today
        print tomorrow
        ret = {
            "total_orders": Order.objects.all().count(),
            "total_users": Profile.objects.all().count() - 1,
            "orders": Order.objects.all().filter(createTime__gte=today).filter(createTime__lt=tomorrow).count(),
            "users": Profile.objects.all().filter(registerTime__gte=today).filter(registerTime__lt=tomorrow).count(),
        }
        return Response(ret, status=status.HTTP_200_OK)


class StatisticsOrder(RetrieveAPIView):
    '''
    used in webadmin
    return the order statistics
    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


    def retrieve(self, request, *args, **kwargs):
        end = datetime.now().date()
        start = end - timedelta(7)
        delta = timedelta(days=1)
        orderdata = []
        d = start
        while d <= end:
            item = []
            s = d
            e = s + delta
            o = Order.objects.all().filter(createTime__gte=s).filter(createTime__lt=e).count()
            item.append(time.mktime(d.timetuple()) * 1000)
            item.append(o)
            orderdata.append(item)
            d += delta


        ret = {
            "label": "Orders",
            "data": orderdata,
        }

        return Response(ret, status=status.HTTP_200_OK)

class StatisticsUsers(RetrieveAPIView):
    '''
    used in webadmin
    return the order statistics
    '''
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        end = datetime.now().date()
        start = end - timedelta(7)
        delta = timedelta(days=1)
        userdata = []
        d = start
        while d <= end:
            item = []
            s = d
            e = s + delta
            o = Profile.objects.all().filter(registerTime__gte=s).filter(registerTime__lt=e).count()
            item.append(time.mktime(d.timetuple()) * 1000)
            item.append(o)
            userdata.append(item)
            d += delta


        ret = {
            "label": "New Users",
            "data": userdata,
        }

        return Response(ret, status=status.HTTP_200_OK)

class userRequestBook(RetrieveUpdateAPIView):
    '''
    for weixin user to request book which we do not have 
    '''
    queryset = RequestBookInfo.objects.all()

    authentication_class = (BasicAuthentication,SessionAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestBookInfoSerializer

        #api for wx users create a new bookrequest information
    def put(self, request, *args, **kwargs):
        print "+++ bookrequest put +++"
        print request.data 

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print "valid"
            serializer.save(user=request.user.profile)
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def requestbook_page(request, format=None):
    if request.method == "GET":
        return render(request, 'p_requestbook.html')




class requestbooklist(ListAPIView):
    queryset = RequestBookInfo.objects.all()
    serializer_class = RequestBookInfoSerializer

    authentication_classes = ( BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('createTime')
    ordering = ['-createTime', ]

    def list(self, request, *args, **kwargs):

        status = request.GET['status']
        if status:
            objects = RequestBookInfo.objects.filter(status=status)
        else:
            objects = RequestBookInfo.objects.all()

        objects = self.filter_queryset(objects)


        

        recordsTotal = objects.count()

        recordsFiltered = recordsTotal

        start = int(request.GET['start'])
        length = int(request.GET['length'])
        draw = int(request.GET['draw'])

        # filter objects according to user inputs

        objects = objects[start:(start + length)]


        serializer = self.get_serializer(objects, many=True)
        # dic = [obj.as_dict() for obj in objects]


        resp = {
            'draw': draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsFiltered,
            'data': serializer.data,
        }

        return HttpResponse(json.dumps(resp), content_type="application/json")


