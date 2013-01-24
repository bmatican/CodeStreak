from django.http import HttpResponse, Http404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import Http404
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse as url_reverse

import json

from CodeStreak.xhpy import *
from CodeStreak.contests.models import *


def getScores():
  return {
            'scores' : 'scores',
         }


def getLogs():
  return {
            'logs' : 'logs',
         }

data_providers = {
  'getScores' : getScores,
}

restricted_data_providers = {
  'getLogs' : getLogs,
}

def pula(request):
  global data_providers
  if request.is_ajax() and request.method == 'POST':
    action = request.POST.get('action', '')
    response = None
    if action in data_providers:
      data_function = data_providers.get(action)
      response = data_function()
    if (response == None and action in restricted_data_providers and
        request.user.is_staff):
      data_function = restricted_data_providers.get(action)
      response = data_function()
    if response == None:
      raise Http404
    else:
      return HttpResponse(json.dumps(response))
  else:
    raise Http404


def contest_list(request):
  limit = request.GET.get('limit')
  offset = request.GET.get('offset')
  contests = Contest.get_all_contests(offset, limit)

  title = 'CodeStreak'

  page = \
  <cs:page title={title}>
    <cs:header-home />
    <cs:content>
      <h2>Contest List</h2>
      <cs:contest-list contests={contests} />
    </cs:content>
    <cs:footer />
  </cs:page>

  return HttpResponse(str(page))


@login_required
def contest_home(request, contest_id):
  user_id = request.user.id

  try:
    scores = Score.get_visible_scores(contest_id, user_id)

    page = ''
    for s in scores:
      page += '{} -> {} -> {}\n'.format(s.task.id, s.task.difficulty, s.score)
    return HttpResponse(str(page))
  except:
    return Http404


def contest_ranking(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  title = 'CodeStreak - {}'.format(contest.name)

  tasks = contest.assigned_tasks.all()
  users = contest.registered_users.all()

  content = ''
  content += '<p>{}</p>'.format(contest)
  content += '<p>Tasks</p>'
  content += '<ul>'
  for t in tasks:
    content += '<li>{}</li>'.format(t)
  content += '</ul>'

  content += '<p>Users</p>'
  content += '<ul>'
  for u in users:
    content += '<li>{}</li>'.format(u)
  content += '</ul>'

  page = \
  <cs:page title={title}>
    <cs:header-contest contest={contest} active_home={False} />
    <cs:content>
      <textarea>{content}</textarea>
    </cs:content>
    <cs:footer />
  </cs:page>

  return HttpResponse(str(page))


@require_POST
@login_required
def register_to_contest(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
    Participation.register_user(contest_id, request.user.id)
  except Contest.DoesNotExist:
    raise Http404
  except IntegrityError:
    return HttpResponse("You are already signed up for this contest!")

  page = ''
  page += '<p>Registration complete for {}</p>'.format(contest)
  return HttpResponse(str(page))


@require_POST
@login_required
def unregister_from_contest(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
    Participation.unregister_user(contest_id, request.user.id)
  except Contest.DoesNotExist:
    raise Http404
  except Participation.DoesNotExist:
    return HttpResponse("You are not signed up for this contest!")

  page = ''
  page += '<p>You are no longer registered for {}</p>'.format(contest)
  return HttpResponse(str(page))
