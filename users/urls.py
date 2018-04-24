from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='login')
#    url(r'^/$', views.loginView.as_view(), name='login'),
    url(r'^login/$', views.wxlogin, name='login'),
    url(r'^list/$', views.UserList.as_view(), name='UserList'),
    url(r'^$', views.User, name='User'),
    # address related 
    url(r'address/$', views.address.as_view(), name='addressView'),
    url(r'^profile/(?P<pk>\d+)/$', views.profile.as_view(), name='profileView'),
    url(r'address/default/$', views.getDefaultAddress.as_view(),name="defaultAddress"),
    url(r'address/list/$', views.wxaddressList.as_view(),name="defaultAddress"),
    url(r'address/list/(?P<pk>\d+)$', views.webaddressList.as_view(),name="defaultAddress"),

    # searchinfo related
    url(r'^searchinfo/$', views.searchInfo, name='searchInfo'),
    url(r'^searchinfo/list/$', views.searchInfoList.as_view(), name='userSearchInfoList'),

    # user request book info 
    url(r'^request/$', views.requestbook_page, name='requestbookPage'),
    url(r'^requestbookinfo/api/create/$', views.userRequestBook.as_view(), name='userRequestBook'),
    url(r'^request/list/$', views.requestbooklist.as_view(), name='userRequestBook'),

]