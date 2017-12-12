from django.conf.urls import url
from . import views

from django.views.generic import TemplateView
urlpatterns = [
#    url(r'^$', views.index, name='login')
    url(r'^$', views.loginView.as_view(), name='login'),
    url(r'^index', views.index, name='index'),

]