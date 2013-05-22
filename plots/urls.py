from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView

urlpatterns = patterns('',
        url(r'^$', TemplateView.as_view(template_name="plots_index.html")),
        )

####### Boxfill #######
urlpatterns += patterns('plots.boxfill',
        url(r'^boxfill/$', 'boxfill'),
)