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
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, renderers, status, filters
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sku.models import Book, LibBook, Banner, Category, Coupon, Notice
from uploadimages.models import UploadedImage
from .filter import BookFilter, LibBookFilter
from .form import UploadFileForm, bookAddForm, libBookAddForm
from .serialize import BannerSerializer, BooklistSerializer, LibbookSerializer, CategorySerializer, CouponSerializer, \
    NoticeSerializer
from .tools import download_photo


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
        try:
            result = super(bookDeleteView, self).delete(request, *args, **kwargs)
            messages.success(self.request, '[书籍 删除成功] !')
        except ProtectedError as exception:
            raise Exception('This book is related.')

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
                name = form.cleaned_data['name']
                press = form.cleaned_data['press']
                author = form.cleaned_data['author']
                price = form.cleaned_data['price']
                isbn = form.cleaned_data['isbn']

                imageurl = form.cleaned_data['imageurl']
                filename = str(isbn) + ".jpg"
                ret = download_photo(imageurl, filename)

                if Book.objects.filter(isbn = isbn).exists():
                    error = "ISBN %d book exist !" %(isbn)
                else:
                    success = "True"
                    b = Book(name=name, press=press, author=author, price=price, isbn=isbn, cover="lpic/" + filename)
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

    return str((float(s))) if s else ""

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
        isbn = r['isbn13']
        press = r['publisher']
        price = r['price']
        price = getPrice(price)
        author = r['author']
        author = author[0] if author else ""
        image = r['images']['large']
        if r['subtitle']:
            name = r['title'] + '--' + r['subtitle']
        else:
            name = r['title']
        rst = {
            'name': name ,
            'press' : press,
            'author' : author,
            'isbn': isbn,
            'price': price,
            'image': image
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

            serialize = BooklistSerializer(objects, many=True)


            resp = {
                'draw': draw,
                'recordsTotal': recordsTotal,
                'recordsFiltered': recordsFiltered,
                'data': serialize.data,
            }

            return HttpResponse(json.dumps(resp), content_type="application/json")



def libraryBookImport(isbn, uuid):
    book = Book.objects.get(isbn=isbn)
    book.libbook_set.create(uuid=uuid)
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
                    serializer = BooklistSerializer(book)
                    r.append(serializer.data)

            resp = {
                'status': status,
                'msg': msg,
                'bindbook': r,
            }
            
            return HttpResponse(json.dumps(resp), content_type="application/json")

class libBook(generic.View):
    def get(self, request):

        return render(request, 'p_libbooks.html')

    def post(self, request):

        objects = LibBook.objects.all()

        recordsTotal = objects.count()
        recordsFiltered = recordsTotal

        start = int(request.POST['start'])
        length = int(request.POST['length'])
        draw = int(request.POST['draw'])

        # filter objects according to user inputs
        serializer = LibbookSerializer(objects, many=True)

        objects = LibBookFilter(request.POST, queryset=objects)

        recordsFiltered = objects.qs.count()

        objects = objects.qs[start:(start + length)]

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


class libBookQuery(generics.ListAPIView):
    queryset = LibBook.objects.all()
    serializer_class = LibbookSerializer

    authentication_classes = ( BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('status', 'book__isbn',)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def coupons_page(request, format=None):
    if request.method == "GET":
        return render(request, 'p_coupons.html')


class CouponsQuery(generics.ListAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    authentication_classes = ( BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = ('createTime')
    ordering = ['-createTime', ]

    def list(self, request, *args, **kwargs):
        objects = Coupon.objects.all()
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

class libbookUpdate(generics.RetrieveUpdateDestroyAPIView):
    # Get /Update /Delete a libbook
    queryset = LibBook.objects.all()
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'p_libbookdetail.html'
    serializer_class = LibbookSerializer

    authentication_classes = ( BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


    def retrieve(self, request, *args, **kwargs):
        uuid = kwargs.pop('uuid')
        libbook = get_object_or_404(LibBook, uuid=uuid)
        serializer = LibbookSerializer(libbook)
        return Response({'libbook': serializer.data})

    def update(self, request, *args, **kwargs):
        '''
        只允许更改 UUID 和 状态
        '''
        print (" +++ libbookUpdate -update +++")
        uuid = kwargs['uuid']
        libbook = get_object_or_404(LibBook, uuid=uuid)

        serializer = LibbookSerializer(libbook, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        resp = {
            'code': 0,
            'msg': "OK",
            "data": serializer.data
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    def delete(self, request, *args, **kwargs):
        uuid = kwargs['uuid']
        libbook = get_object_or_404(LibBook, uuid=uuid)

        serializer = LibbookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        libbook.delete()

        resp = {
            'code': 0,
            'msg': "OK",
            "data": []
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")        

class bannerList(generic.View):
    def get(self, request):
        objects = Banner.objects.all()
        serialize = BannerSerializer(objects, many=True)
        return HttpResponse(json.dumps(serialize.data), content_type="application/json")

    def post(self, request):
        pass


class banner(generic.View):
    def get(self, request):
        return render(request, 'p_banners.html')

    def post(self, request):
        '''
        add banner item
        :param request : book isbn
        :return: redirect to the banner list page
        '''
        dumpRequest(request)
        isbn = request.POST['ISBN']
        print "isbn = %s" % isbn

        if isbn:
            book = Book.objects.filter(isbn=int(isbn))
            if book.exists():
                banner = Banner(book=book[0])
                banner.save()
            else:
                messages.error(self.request, '[书籍: %s] 不存在!' % (isbn))
        else:
            messages.error(self.request, '请输入ISBN')

        dic = []
        return redirect('sku:banner')

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



#####Test only
class batchaddBook(generic.View):
    def get(self, request):
        if request.method == "GET":

            return render(request, 'p_bookbatchadd.html')

    def post(self, request):
        if request.method == "POST":
            print(" +++ batchaddBook +++")
            error = ''
            success = ''
            dumpRequest(request)

            books = Book.objects.get(isbn=9787111579489)
            print books.desc
            print request.POST['content']
            books.desc = request.POST['content']
            books.save()

            resp = {
                'code': 0,
                'msg': "OK",
                "data": []
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")       

@csrf_exempt
def uploadimages(request):
    dumpRequest(request)
    resp = {
        'jsonrpc' : '2.0',
        'result' : [],
        'id' : "id"
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")       




class restbookUpdate(generics.RetrieveUpdateDestroyAPIView):
    # Get /Update /Delete a libbook
    queryset = Book.objects.all()
    serializer_class = BooklistSerializer
    lookup_field = 'isbn'
    
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'p_bookdetail.html'

    def retrieve(self, request, *args, **kwargs):
        isbn = kwargs.pop('isbn')
        book = get_object_or_404(Book, isbn=isbn)
        serializer = BooklistSerializer(book, fields={'name','isbn','author','press','price','desc', 'cid'})

        return Response({'book': serializer.data})


    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}     

        resp = {
                'code': 0,
                'msg': "OK",
                "data": []
        }
        return  HttpResponse(json.dumps(resp), content_type="application/json")       


class restaddBook(APIView):
    # add boook
    def get(self, request, format=None):
        return render(request, 'p_bookAdd.html')
    def post(self, request, format=None):
        serializer = BooklistSerializer(data=request.data, fields={'name','author','press','price','isbn','desc','cid'})
        isbn = request.POST['isbn']
        # make sure the users commit SKU pictures 
        pics = UploadedImage.objects.filter(isbn=isbn)
        if not pics.count():
            return Response("请先上传图片", status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError as exception:
                return Response(exception.message, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((SessionAuthentication,BasicAuthentication))
@permission_classes((IsAuthenticated,))
def createLibbook(request, format=None):
    isbn = request.POST['isbn']
    amount = request.POST['amount']
    online = request.POST['online']

    print isbn,amount,online

    book = Book.objects.get_or_none(isbn=isbn)
    if book:
        for i in range(int(amount)):
            if int(online):
                print "create online libbook "
                book.libbook_set.create(status=LibBook.STATUS_ONLINE)
            else:
                print "create offline libbook"
                book.libbook_set.create(status=LibBook.STATUS_OFFLINE)

    else:
        print "can not find book"
    return Response({"status":"OK"},status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def category_view(request, format=None):
    if request.method == "GET":
        return render(request, 'p_category.html')

    if request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            print "catery add +"
            print serializer.validated_data
            serializer.save()
            return redirect('sku:category')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class categoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (TokenAuthentication, BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

class category(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

class webCategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)




class CreateNotice(generics.CreateAPIView):
    # Create Notice for admin
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

class ListNotice(generics.ListAPIView):
    # list notices for admin  
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

class DeleteNotice(generics.DestroyAPIView):
    # Delete a notice for admin 
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)



