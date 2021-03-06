from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  url(r'^admin/', include(admin.site.urls)),

  url(r'^$', 'CodeStreak.contests.views.contest_list',
      name='contest-list'),

  url(r'^facebook/', include('django_facebook.urls')),
  url(r'^accounts/login/$', 'CodeStreak.contests.views.login_view',
      name='auth_login'),
  url(r'^accounts/login/success/$',
      'CodeStreak.contests.views.login_success_view',
      name='auth_login_success'),
  url(r'^accounts/logout/$', 'CodeStreak.contests.views.logout_view',
      name='auth_logout'),

  url(r'^contest/(?P<contest_id>\d+)/register$',
      'CodeStreak.contests.views.register_to_contest',
      name='contest-register'),
  url(r'^contest/(?P<contest_id>\d+)/unregister$',
      'CodeStreak.contests.views.unregister_from_contest',
      name='contest-unregister'),

  url(r'^contest/(?P<contest_id>\d+)/start$',
      'CodeStreak.contests.views.start_contest',
      name='contest-start'),
  url(r'^contest/(?P<contest_id>\d+)/stop$',
      'CodeStreak.contests.views.stop_contest',
      name='contest-stop'),
  url(r'^contest/(?P<contest_id>\d+)/pause$',
      'CodeStreak.contests.views.pause_contest',
      name='contest-pause'),

  url(r'^contest/(?P<contest_id>\d+)$',
      'CodeStreak.contests.views.contest_home',
      name='contest-home'),

  url(r'^contest/(?P<contest_id>\d+)/problems$',
      'CodeStreak.contests.views.contest_problems',
      name='contest-problems'),

  url(r'^contest/(?P<contest_id>\d+)/ranking$',
      'CodeStreak.contests.views.contest_ranking',
      name='contest-ranking'),

  url(r'^contest/(?P<contest_id>\d+)/admin$',
      'CodeStreak.contests.views.contest_admin',
      name='contest-admin'),

  url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
      'document_root': settings.MEDIA_ROOT,
  }),

  url(r'^data_provider/(?P<action>.+)$',
      'CodeStreak.contests.views.data_provider'),
)
