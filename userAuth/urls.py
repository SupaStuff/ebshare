from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.user_login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/$', views.user_profile, name='profile'),
    url(r'^addBook/$', views.addBook, name='addBook'),
    url(r'^addPic/$', views.addPic, name='addPic'),
    url(r'^badWord/$', views.badWord, name='badWord'),


]