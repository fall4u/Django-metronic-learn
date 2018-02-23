# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from rest_framework import renderers, status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.
from .cons import Constant
from .form_user_login import UserForm
from .models import Profile, Address
from .serialize import UserProfileSerializer, AddressSerializer
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
                return redirect("index.html")
            else:
                raise Http404("User is not invalid")
        else:
            print form.errors
#            return HttpResponse("form is not valid")

#def login(request):
#    return render(request, "page_user_login_1.html")

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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print serializer.data
        return Response(serializer.data)



class User(generic.View):
    def get(self, request):
        return render(request, 'p_users.html')

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









