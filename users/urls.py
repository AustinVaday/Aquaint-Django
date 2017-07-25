from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<user>[.-_\w-]+)/$', views.info, name='info')
]
