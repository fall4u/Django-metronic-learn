from django.conf.urls import url

from . import views

app_name = 'sku'

urlpatterns = [
    url(r'^$', views.SkuView.as_view(), name='sku'),
    # download sku template
    url(r'^download/$', views.download, name='download'),
    # sku import / add
    url(r'^skuimport/$', views.skuimport.as_view(), name='skuimport'),

    #  book query 
    url(r'^book/query/$', views.books.as_view(), name='books'),

    # get book information from douban v2.api
    url(r'^book/getinfo/$', views.getBookInfo.as_view(),name='getBookinfo_douban'),

    # add book 
    url(r'^add/$', views.addBook.as_view(), name='addBook'),

    # Update book
    url(r'^book/update/(?P<pk>\d+)/$', views.bookUpdate.as_view(), name='bookUpdate'),

    # Delete book
    url(r'^book/delete/(?P<pk>\d+)/$', views.bookDeleteView.as_view(), name='bookDelete'),

    # library book query
    url(r'^libraryBook/$', views.libBook.as_view(), name='libBook'),

    url(r'^libraryBook/add/$', views.libaddBook.as_view(), name='libaddBook'),

    url(r'^libraryBook/uuid/$', views.bookuuidview.as_view(), name='bookuuid'),
]