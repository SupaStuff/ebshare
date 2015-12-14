from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.renderbookshelf, name='bookshelf'),
    url(r'^/invites$', views.invites, name='invites'),
]
