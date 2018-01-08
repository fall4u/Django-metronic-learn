# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import os.path

from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .form import UploadFileForm, bookAddForm
from .models import Book


# Create your views here.

class SkuView(generic.View):

    def get(self, request):
        items = []
        testline = {}


        books = Book.objects.all()
        recordsTotal = books.count()
        recordsFiltered = recordsTotal
        dic = [obj.as_dict() for obj in books]
        # draw = int(request.GET['draw'])

        resp = {
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsFiltered,
            'data': dic,
        }

        #    return HttpResponse(json.dumps(resp), content_type="application/json")
        return render(request, 'p_books.html')

    #    return render(request, 'p_books.html', {'items': books})

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

    if (filter_author):
        objects = objects.filter(author__contains=filter_author)

    if (filter_press):
        objects = objects.filter(press__contains=filter_press)

    if (filter_isbn):
        objects = objects.filter(isbn__contains=filter_isbn)

    if (filter_name):
        objects = objects.filter(name__contains=filter_name)                


    return objects


class addBook(generic.View):
    def get(self, request):
        if request.method == "GET":
            print "addBook get GET reqeuest"
            dumpRequest(request)
            return render(request, 'p_bookAdd.html');

    def post(self, request):
        if request.method == "POST":
            error = ''
            print "addBook form enter +++"
            dumpRequest(request)

            form = bookAddForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']
                press = form.cleaned_data['press']
                author = form.cleaned_data['author']
                isbn = form.cleaned_data['isbn']
                price = form.cleaned_data['price']

                # book_inst = Book(**form.cleaned_data)
                # book_inst.save(commit = True)

                resp = {
                    'success': "True",
                    'error': error
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")

                # return redirect('addBook')
                # return HttpResponse(json.dumps(resp), content_type="application/json")
                # return HttpResponseRedirect(reverse(addBook.as_view()))
                #   return redirect('sku:addBook')

class books(generic.View):
    def get(self, request):
        if request.method == "GET":
            dumpRequest(request)
            # filter objects according to user inputs
            objects = Book.objects.all()

            dic = [obj.as_dict() for obj in objects]

            resp = {

                'data': dic,
            }
            print resp

            return HttpResponse(json.dumps(dic), content_type="application/json")

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
