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

from sku import urls as sku_urls
from ueditor import urls as ueditor_urls
from uploadimages import urls as uploadimage_urls
from users import views as users_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # homepage
#    url(r'^login/', include('users.urls')),
    url(r'^$', users_views.loginView.as_view()),
    url(r'index.html/', users_views.index),

    url(r'user/',include('users.urls')),

    # sku
    url(r'^sku/', include(sku_urls)),

    # ueditor
    url(r'^controller/', include(ueditor_urls)),

    # uploadimage 
    url(r'^uploadimage/', include(uploadimage_urls)),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
