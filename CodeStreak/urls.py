from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  # Examples:
  # url(r'^$', 'CodeStreak.views.home', name='home'),
  # url(r'^CodeStreak/', include('CodeStreak.foo.urls')),

  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^facebook/', include('django_facebook.urls')),
  url(r'^accounts/', include('django_facebook.auth_urls')),

  url(r'^test/(?P<test_id>\d+)', 'CodeStreak.contests.views.test'),
  url(r'^test', 'CodeStreak.contests.views.test'),

  url(r'^contest/(?P<contest_id>\d+)/register/(?P<user_id>\d+)', 'CodeStreak.contests.views.register_to_contest'),
  url(r'^contest/(?P<contest_id>\d+)', 'CodeStreak.contests.views.display_contest'),
  url(r'^contest', 'CodeStreak.contests.views.display_contest'),

  url(r'^pula', 'CodeStreak.contests.views.pula'),
)
