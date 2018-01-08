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

    # add book 
    url(r'^add/$', views.addBook.as_view(), name='addBook')

]