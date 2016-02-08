from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.renderHome, name='home'),
    url(r'^about/$', views.renderAbout, name='about'),
]
