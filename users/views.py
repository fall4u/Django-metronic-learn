# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.views import generic
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
# Create your views here.

from .form_user_login import  UserForm
#class loginView(generic.View):

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