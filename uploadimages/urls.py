from django.conf.urls import url

from . import views

app_name = 'uploadimages'

urlpatterns = [
    url(r'^$', views.uploadimages.as_view(), name='uploadimages'),
    url(r'^list/(?P<isbn>\d+)/$', views.imageList.as_view(), name='imageList'),    
    url(r'^move_up/$', views.imagesMoveUp, name='imagesUp'),
    url(r'^move_down/$', views.imagesMoveDown, name='imagesDown'),
]

