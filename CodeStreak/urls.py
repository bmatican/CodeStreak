from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Examples:
  # url(r'^$', 'CodeStreak.views.home', name='home'),
  # url(r'^CodeStreak/', include('CodeStreak.foo.urls')),

  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  (r'^facebook/', include('django_facebook.urls')),
  (r'^accounts/', include('django_facebook.auth_urls')), 
)