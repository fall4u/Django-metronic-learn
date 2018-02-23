from django.conf.urls import url

from . import views

app_name = 'order'

urlpatterns = [
#    url(r'^$', views.index, name='login')
#    url(r'^/$', views.loginView.as_view(), name='login'),
    url(r'^create/$', views.order.as_view(), name='create'),
    url(r'^list/$', views.orderList.as_view(),name='list'),
    url(r'^fee/$', views.orderFee.as_view(), name='getfee'),

]