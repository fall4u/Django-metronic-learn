# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import os.path

import requests
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView

from sku.models import Book, LibBook
from .form import UploadFileForm, bookAddForm, libBookAddForm


# Create your views here.

class SkuView(generic.View):

    def get(self, request):
        items = []
        testline = {}

        books = Book.objects.all()
        if (books):
            recordsTotal = books.count()
            recordsFiltered = recordsTotal
            dic = [obj.as_dict for obj in books]
            # draw = int(request.GET['draw'])

            resp = {
                'recordsTotal': recordsTotal,
                'recordsFiltered': recordsFiltered,
                'data': dic,
            }

        #    return HttpResponse(json.dumps(resp), content_type="application/json")
        return render(request, 'p_books.html')


    def post(self, request):
        pass


def dumpRequest(request):
    if request.method == "POST":
        for key in request.POST:
            print key
            value = request.POST.getlist(key)
            print value
    else:
        for key in request.GET:
            print key
            value = request.GET.getlist(key)
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


class bookUpdate(UpdateView):
    model = Book
    fields = ['name', 'author', 'price', 'isbn', 'press']
    template_name = "p_bookdetail.html"
    success_url = reverse_lazy('sku:sku')

    def form_valid(self, form):
        result = super(bookUpdate, self).form_valid(form)

        if form.has_changed():
            messages.success(self.request, '[书籍: %s] 信息修改成功!'%(form.cleaned_data['isbn']))
        return result

class bookDeleteView(DeleteView):
    '''
    TODO:
        if the book has library book instance, and then
        user can not delete it
    '''
    model = Book

    success_url = reverse_lazy('sku:sku')
    template_name = "p_bookdelete.html"

    def delete(self, request, *args, **kwargs):
        result = super(bookDeleteView, self).delete(request, *args, **kwargs)
        messages.success(
            self.request, '[书籍 删除成功] !')
        return result

    def get_book(self):
        return model_to_dict(self.get_object())


class addBook(generic.View):
    def get(self, request):
        if request.method == "GET":
            print "addBook get GET reqeuest"
            dumpRequest(request)
            return render(request, 'p_bookAdd.html')

    def post(self, request):
        if request.method == "POST":
            error = ''
            success = ''
            dumpRequest(request)

            form = bookAddForm(request.POST)

            if form.is_valid():
                # name = form.cleaned_data['name']
                # press = form.cleaned_data['press']
                # author = form.cleaned_data['author']
                # price = form.cleaned_data['price']
                isbn = form.cleaned_data['isbn']

                if Book.objects.filter(isbn = isbn).exists():
                    error = "ISBN %d book exist !" %(isbn)
                else:
                    success = "True"
                    b = Book(**form.cleaned_data)
                    b.save()


                resp = {
                    'success': success,
                    'error': error
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")

def isPrice(c):
    r = False
    if (c.isdigit()) or c == '.':
        r = True
    return r

def getPrice(unicodeStr):
    s = unicodeStr.encode('utf-8')
    s = filter(isPrice, s)
    fp = float(s)
    fp = int(fp * 100)
    return str(fp)

def getBookInfo_douban(url):
    isbn = ''
    press = ''
    price = ''
    author = ''
    name = ''
    rst = {}

    r = requests.get(url)
    print r
    if r.status_code == 200:
        r = r.json()
        print r
        isbn = r['isbn13']
        press = r['publisher']
        price = r['price']
        price = getPrice(price)
        author = r['author'][0]
        name = r['title'] + '--' + r['subtitle']
        rst = {
            'name': name ,
            'press' : press,
            'author' : author,
            'isbn': isbn,
            'price': price
        }
    return rst

class getBookInfo(generic.View):
    def get(selfself,request):
        '''
        get book information using douban v2.api
        :param request: isbn
        :return: json value
        '''
        _url = "https://api.douban.com/v2/book/isbn/"
        success = ''
        error = ''
        data = ''
        isbn = request.GET.get('isbn',None)
        print isbn
        r = {}

        if isbn and isbn.isdigit() and len(isbn) == 13:
            success = "True"
            url = _url + isbn
            r = getBookInfo_douban(url)
            if not r:
                success = ''
                error = "Book not existed in douban"

        else:
            error = "ISBN not invalid"

        resp = {
            'success': success,
            'error': error,
            'data': r,
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")


class books(generic.View):
    def get(self, request):
        dumpRequest(request)
        # filter objects according to user inputs
        objects = Book.objects.all()
        isbn = request.GET.get('isbn', None)



        if isbn:
            objects = objects.filter(isbn__contains=isbn)
            dic = [obj.as_dict for obj in objects]
        else:
            dic = []

        resp = {
            "bindbook": dic,
        }

        print dic
        return HttpResponse(json.dumps(resp), content_type="application/json")

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

            dic = [obj.as_dict for obj in objects]

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


def libraryBookImport(isbn, uuid):
    b = LibBook(isbn=isbn, uuid=uuid)
    b.save()

    r = Book.objects.get(isbn=isbn)
    r.totalAmount = r.totalAmount + 1
    r.save()
    return r

class libaddBook(generic.View):
    def get(self, request):
            return render(request, 'p_libbookadd.html')

    def post(self, request):
        if request.method == "POST":
            error = ''
            success = ''
            r = []
            dumpRequest(request)
            print ("+++libaddBook +++")
            form = libBookAddForm(request.POST)

            if form.is_valid():
                isbn = form.cleaned_data['isbn']
                uid  = form.cleaned_data['uuid']

                success = 'True'
                print "isbn : %s"%(isbn)
                print "uid: %s"%(uid)

                if LibBook.objects.filter(uuid=uid).exists():
                    print "if"
                    error = "uid %d book exist !" %(uid)
                elif not Book.objects.filter(isbn=isbn).exists():
                    print "elif not"
                    error = "isbn %d book does not exist !" % (isbn)
                else:
                    print "else true"
                    success = "True"
                    r = libraryBookImport(isbn, uid)

                    resp = {
                        'status': "OK",
                        'msg': "",
                        'bindbook': [r.as_dict]
                    }
            else:
                resp = {
                    'status': "Fail",
                    'msg': "form data is not valid",
                    'bindbook':r
                }

            print resp 
            
            return HttpResponse(json.dumps(resp), content_type="application/json")

class libBook(generic.View):
    def get(self, request):

        return render(request, 'p_libbooks.html')

    def post(self, request):
        dumpRequest(request)

        isIsbnOnly = request.POST.get('isISBN', 'False')

        if isIsbnOnly == 'False':
            print "isIsbnOnly == False"
        else:
            print "isIsbnOnly == True"
            objects = LibBook.objects.all()
            isbn = request.POST['isbn']

            recordsTotal = 0
            recordsFiltered = 0
            dict = {}

            if isbn != 'undefined':
                book = objects.filter(isbn__exact=isbn)
                if book:
                    recordsTotal = 1
                    recordsFiltered = 1
                    dict = book.as_dict()



            resp = {
                'recordsTotal': recordsTotal,
                'recordsFiltered': recordsFiltered,
                'data': dict,
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        objects = LibBook.objects.all()

        recordsTotal = objects.count()
        recordsFiltered = recordsTotal

        start = int(request.POST['start'])
        length = int(request.POST['length'])
        draw = int(request.POST['draw'])


        objects = objects[start:(start + length)]

        dic = [obj.as_dict for obj in objects]

        resp = {
            'draw': draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsFiltered,
            'data': dic,
        }

        return HttpResponse(json.dumps(resp), content_type="application/json")


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
