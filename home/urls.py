from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView

urlpatterns = patterns('home.views',
        url(r'^/?$', 'show_index'),
        url(r'^boxfill/$', 'boxfill'),
)