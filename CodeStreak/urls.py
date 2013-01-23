from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^facebook/', include('django_facebook.urls')),
  url(r'^accounts/', include('django_facebook.auth_urls')),

  url(r'^$', 'CodeStreak.contests.views.contest_list'),
  url(r'^contest/(?P<contest_id>\d+)/register$',
      'CodeStreak.contests.views.register_to_contest'),
  url(r'^contest/(?P<contest_id>\d+)/unregister$',
      'CodeStreak.contests.views.unregister_from_contest'),

  url(r'^contest/(?P<contest_id>\d+)$',
      'CodeStreak.contests.views.contest_ranking'),

  url(r'^pula', 'CodeStreak.contests.views.pula'),
)
