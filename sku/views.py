# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import json
import os.path
import uuid

import qrcode
import requests
from django.conf import settings
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import UpdateView, DeleteView

from sku.models import Book, LibBook
from .filter import BookFilter, LibBookFilter
from .form import UploadFileForm, bookAddForm, libBookAddForm


# Create your views here.

class SkuView(generic.View):

    def get(self, request):
        # items = []
        # testline = {}
        #
        # books = Book.objects.all()
        # if (books):
        #     recordsTotal = books.count()
        #     recordsFiltered = recordsTotal
        #     dic = [obj.as_dict for obj in books]
        #     # draw = int(request.GET['draw'])
        #
        #     resp = {
        #         'recordsTotal': recordsTotal,
        #         'recordsFiltered': recordsFiltered,
        #         'data': dic,
        #     }

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
        if r['subtitle']:
            name = r['title'] + '--' + r['subtitle']
        else:
            name = r['title']
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
            #            dumpRequest(request)

            objects = Book.objects.all()

            recordsTotal = objects.count()
            recordsFiltered = recordsTotal

            start = int(request.POST['start'])
            length = int(request.POST['length'])
            draw = int(request.POST['draw'])

            # filter objects according to user inputs
            objects = BookFilter(request.POST, queryset=objects)

            recordsFiltered = objects.qs.count()
            objects = objects.qs[start:(start + length)]

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
    book = Book.objects.get(isbn=isbn)

    book.libbook_set.create(uuid=uuid)

    book.totalAmount = book.libbook_set.count()
    book.save()
    return book


def makeqrcode():
    uid = uuid.uuid1()
    strUid = str(uuid.uuid1())

    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10,
                       border=4)
    qr.add_data(strUid)
    img = qr.make_image()
    Name = strUid + ".png"
    fullname = os.path.join(settings.MEDIA_ROOT, Name)
    img.save(fullname)
    return Name


def get_qrimageset(num):
    qs = []
    record = {}

    for i in range(num):
        name = makeqrcode()
        print "name = %s" % (name)
        record['imagesrc'] = name
        record['desc'] = name.split('.')[0]
        qs.append(record.copy())

    return qs


class bookuuidview(generic.View):
    def get(self, request):
        uuidinfo = get_qrimageset(24)
        return render(request, 'p_uuid.html',  {'uuidinfo': uuidinfo})

class libaddBook(generic.View):
    def get(self, request):
            return render(request, 'p_libbookadd.html')

    def post(self, request):
        if request.method == "POST":
            status = ''
            msg = ''
            r = []
            dumpRequest(request)
            form = libBookAddForm(request.POST)

            if form.is_valid():
                isbn = form.cleaned_data['isbn']
                uid  = form.cleaned_data['uuid']

                success = 'True'
                print "isbn : %s"%(isbn)
                print "uid: %s"%(uid)

                if LibBook.objects.filter(uuid=uid).exists():
                    msg = "uid %d book exist !" %(uid)
                    status = "Fail"
                elif not Book.objects.filter(isbn=isbn).exists():
                    msg = "isbn %d book does not exist !" % (isbn)
                    status = "Fail"                    
                else:
                    status = "OK"
                    msg = "Bind book success !!"
                    book = libraryBookImport(isbn, uid)
                    r = [book.as_dict]

            resp = {
                'status': status,
                'msg': msg,
                'bindbook':r
            }

            print resp 
            
            return HttpResponse(json.dumps(resp), content_type="application/json")

class libBook(generic.View):
    def get(self, request):

        return render(request, 'p_libbooks.html')

    def post(self, request):
        dumpRequest(request)

        objects = LibBook.objects.all()

        recordsTotal = objects.count()
        recordsFiltered = recordsTotal

        start = int(request.POST['start'])
        length = int(request.POST['length'])
        draw = int(request.POST['draw'])

        # filter objects according to user inputs
        objects = LibBookFilter(request.POST, queryset=objects)

        recordsFiltered = objects.qs.count()

        objects = objects.qs[start:(start + length)]

        dic = [obj.as_dict() for obj in objects]


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
