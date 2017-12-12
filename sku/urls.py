from django.conf.urls import url
from . import views

from django.views.generic import TemplateView
urlpatterns = [
    url(r'^', views.SkuView.as_view(), name='sku'),

]