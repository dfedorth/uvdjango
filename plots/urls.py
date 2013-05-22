from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('',
        url(r'^/$', ))

urlpatterns += patterns('plots.boxfill',
        url(r'^boxfill/$', 'boxfill'),
)