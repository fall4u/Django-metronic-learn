# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import os.path

from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .form import UploadFileForm
from .models import Book


# Create your views here.

class SkuView(generic.View):

    def get(self, request):
        items = []
        testline = {}

        # for i in range(100):
        #     testline['bookname'] = "Python Web开发测试驱动方法"
        #     testline['press'] = "人民邮电出版社"
        #     testline['lendCount'] = 4
        #     testline['amount'] = 5
        #     testline['author'] = "Harry J.W. Percival"
        #     testline["importTime"] = "2017/12/29"
        #     testline["status"] = "busy"
        #     testline["class"] = "IT"
        #     items.append(testline.copy())

        books = Book.objects.all()

        return render(request, 'p_books.html')

    #        return render(request, 'p_books.html', {'items': books})

    def post(self, request):
        pass


def dumpRequest(request):
    if request.method == "POST":
        for key in request.POST:
            print key
            value = request.POST.getlist(key)
            print value


def filter_books(objects, request):
    filter_author = request.POST['author']
    filter_press = request.POST['press']
    filter_isbn = request.POST['isbn']
    filter_name = request.POST['name']
    filter_status = request.POST['status']

    if (filter_status):
        objects = objects.filter(status__exact=filter_status)

    return objects

class books(generic.View):
    def post(self, request):
        if request.method == "POST":
            dumpRequest(request)

            objects = Book.objects.all()

            recordsTotal = objects.count()
            recordsFiltered = recordsTotal

            start = int(request.POST['start'])
            length = int(request.POST['length'])
            draw = int(request.POST['draw'])

            filter_author = request.POST['author']
            filter_press = request.POST['press']
            filter_isbn = request.POST['isbn']
            filter_name = request.POST['name']
            filter_status = request.POST['status']

            if (filter_author):
                print filter_author
            else:
                print "author empty"

            if (filter_press):
                print filter_press
            else:
                print "press empty"
            if (filter_isbn):
                print filter_isbn
            else:
                print "isbn empty"

            if (filter_name):
                print filter_name
            else:
                print "name empty"
            if (filter_status):
                print filter_status
            else:
                print "status empty"
            # filter objects according to user inputs
            objects = filter_books(objects, request)
            recordsFiltered = objects.count()

            objects = objects[start:(start + length)]

            dic = [obj.as_dict() for obj in objects]

            resp = {
                'draw': draw,
                'recordsTotal': recordsTotal,
                'recordsFiltered': recordsFiltered,
                'data': dic,
            }

            return HttpResponse(json.dumps(resp), content_type="application/json")

            # dumpRequest(request)

            # form = bookQueryForm(request.POST)

            # if form.is_valid():
            #     print "form is valid"
            #     author = form.cleaned_data["author"]
            #     if author:
            #         print "author is not emptye " + author
            #     else:
            #         print "author is empty" + author
            # else:
            #     print "form is not valid "
            #     print form.error_detail()

            # return render(request, 'p_test.html', {'form': form})

            # return HttpResponse("ok")



class skuimport(generic.View):
    def get(self, request):
        pass

    def post(self, request):
        print "skuimport POST +++"
        if request.method == "POST":
            print "sku skuimport"
            dumpRequest(request)

            form = UploadFileForm(request.POST, request.FILES)

            if form.is_valid():
                print "form is valid"
                handle_uploaded_file(request.FILES['skufile'], "skufile.jpg")
            else:
                print "form is not valid"

            # if request.FILES:
            #     print " we have request files "
            #     handle_uploaded_file(request.FILES['skufile'], "skufile")
            # else:
            #     print "request files is null "
            return render(
                request,
                'p_test.html',
                {'form': form}
            )
            # return HttpResponse("ok")


def handle_uploaded_file(file, filename):
    print (" +++ handle_uploaded_file +++")
    if not os.path.exists('upload/'):
        os.mkdir('upload/')

    with open('upload/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    print (" --- handle_uploaded_file ---")

def somevie(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response


def ptest(request):
    return HttpResponse("Hello, world. ptest")


def download(request, download_id=''):
    # do something
    filepath = "/Users/zhuxufeng/Dev/django/shangqu/sku/shangQuProductImportTemp.xls"
    the_file_name = os.path.basename(filepath)  # 显示在弹出对话框中的默认的下载文件名
    # filename=a.path                    #要下载的文件路径

    fp = open(filepath, 'rb')
    response = HttpResponse(fp.read())
    fp.close()

    response['Content-Length'] = str(os.stat(filepath).st_size)
    #    response=StreamingHttpResponse(readFile(filepath))
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


# Why safari can download the excel file successfully, and chrome/firefox can not  using this method
def readFile(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                print c
                yield c
            else:
                print "break"
                break
