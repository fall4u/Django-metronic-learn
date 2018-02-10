from django.conf.urls import url

from . import views

app_name = 'ueditor'

urlpatterns = [
    url(r'^/$', views.get_ueditor_controller, name='ueditorController'),
]