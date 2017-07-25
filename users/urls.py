from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^_login/$', views.authentication, name='login'),
    url(r'^_login/$', auth_views.login, {'template_name': 'users/userlogin.html'}, name='login'),
    url(r'^_signup/$', views.user_signup, name='signup'),
    url(r'^(?P<user>[.-_\w-]+)/$', views.info, name='info')
]
