# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic

# Create your views here.

class SkuView(generic.View):

    def get(self, request):
        return render(request,"p_skus.html")

