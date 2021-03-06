"""shangqu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from order import urls as order_urls
from sku import urls as sku_urls
from ueditor import urls as ueditor_urls
from uploadimages import urls as uploadimage_urls
from users import views as users_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # homepage
#    url(r'^login/', include('users.urls')),
    url(r'^$', users_views.loginView.as_view()),
#    url(r'index/$', users_views.index, name='index'),
    url(r'index/$', users_views.Statistics.as_view(), name='index'),
    url(r'notice/$', users_views.notice, name='wxnotice'),

    url(r'user/',include('users.urls')),
    url(r'statistics/order/$', users_views.StatisticsOrder.as_view(),name="statisticsOrder"),
    url(r'statistics/users/$', users_views.StatisticsUsers.as_view(), name="statisticsUsers"),

    # sku
    url(r'^sku/', include(sku_urls)),

    # ueditor
    url(r'^controller/', include(ueditor_urls)),

    # uploadimage 
    url(r'^uploadimage/', include(uploadimage_urls)),

    # order
    url(r'^order/', include(order_urls)),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
