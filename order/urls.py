from django.conf.urls import url

from . import views
from . import webviews

app_name = 'order'

urlpatterns = [
#    url(r'^$', views.index, name='login')
#    url(r'^/$', views.loginView.as_view(), name='login'),
    url(r'^api/create/$', views.order.as_view(), name='create'),
    url(r'^api/list/$', views.orderList.as_view(),name='list'),
    url(r'^api/fee/$', views.orderFee.as_view(), name='getfee'),
    url(r'^api/statistics/$', views.orderStatistics.as_view(), name='statstics'),

    # web admin endpoint
    url(r'^$', webviews.webOrderPage, name='webOrderPage'),
    url(r'^list/$',webviews.webOrderList.as_view(),name='webOrderList'),
    url(r'^(?P<pk>\d+)/$', webviews.webOrderDetail.as_view(), name='webOrderDetail'),
    url(r'^statistics/$', webviews.weborderStatistics.as_view(), name='statstics'),


    url(r'^outbooks/$', webviews.webOutbooksPage, name='webOutbooksPage'),
    url(r'^outbooks/list/$', webviews.webOutbooksList.as_view(), name='webOutbooksList'),

]