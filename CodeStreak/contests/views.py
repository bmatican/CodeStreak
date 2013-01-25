from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render_to_response
from django.http import Http404
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse as url_reverse

import json

from CodeStreak.xhpy import *
from CodeStreak.contests.models import *
from CodeStreak.contests.utils.tasks import *


# FIXME: Remove when POST requests is properly supported
def require_POST(f):
    return f

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
  <cs:page request={request} title={title}>
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
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  title = 'CodeStreak - {}'.format(contest.name)
  content = <pre />
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab="contest-home" />
    <cs:content>
      <h2>{'{} Problem Set'.format(contest.name)}</h2>
      {content}
    </cs:content>
    <cs:footer />
  </cs:page>

  user_id = request.user.id
  try:
    scores = Score.get_visible_scores(contest_id, user_id)
    indexed_task_ids = Contest.get_task_ordering(contest_id)
  except Score.DoesNotExist:
    raise Http404
  except Contest.DoesNotExist:
    raise Http404

  seen_ids = [s.task.id for s in scores]
  handler = ProblemHandler(seen_ids, indexed_task_ids)
  tasks = handler.get_visible_tasks()
  # (ind, id) | None | raise exception = handler.get_current_task()
  # handler.is_task_visible(task_id)

  output = ''

  output += '<p>Indexed tasks</p>'
  for ind, id in indexed_task_ids:
    output += '<p>Index {} -> Task_id {}</p>'.format(ind, id)

  output += '<p>Scores</p>'
  for s in scores:
    output += \
      '<p> Task_id {} -> Diff {} -> Score {}</p>'.format(s.task.id, s.task.difficulty, s.score)

  output += '<p>Visible Tasks</p>'
  for id in tasks:
    output += '<p>Task_id {}</p>'.format(id)
  content.appendChild(output)
  return HttpResponse(str(page))


def contest_ranking(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  title = 'CodeStreak - {}'.format(contest.name)
  content = <pre />
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab="contest-ranking" />
    <cs:content>
      <h2>{'{} Ranking'.format(contest.name)}</h2>
      {content}
    </cs:content>
    <cs:footer />
  </cs:page>

  tasks = contest.assigned_tasks.all()
  users = contest.registered_users.all()

  output = ''
  output += '<p>{}</p>'.format(contest)
  output += '<p>Tasks</p>'
  output += '<ul>'
  for t in tasks:
    output += '<li>{}</li>'.format(t)
  output += '</ul>'

  output += '<p>Users</p>'
  output += '<ul>'
  for u in users:
    output += '<li>{}</li>'.format(u)
  output += '</ul>'
  content.appendChild(output)

  return HttpResponse(str(page))


@require_POST
@login_required
def register_to_contest(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
    contest_url = url_reverse('contest-home', args=(contest_id,))
    Participation.register_user(contest_id, request.user.id)
  except Contest.DoesNotExist:
    raise Http404
  except IntegrityError:
    messages.error(request, 'You are already signed up for this contest!')
    return HttpResponseRedirect(contest_url)

  messages.info(request,
      'Registration complete for {}'.format(contest.name))
  return HttpResponseRedirect(contest_url)


@require_POST
@login_required
def unregister_from_contest(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
    contest_url = url_reverse('contest-home', args=(contest_id,))
    Participation.unregister_user(contest_id, request.user.id)
  except Contest.DoesNotExist:
    raise Http404
  except Participation.DoesNotExist:
    messages.error(request, 'You are not signed up for this contest!')
    return HttpResponseRedirect(contest_url)

  messages.info(request,
      'You are no longer registered for {}'.format(contest.name))
  return HttpResponseRedirect(contest_url)


def login_view(request):
  if not request.user.is_authenticated():
    messages.error(request, 'You need to login first.')
  return HttpResponseRedirect(url_reverse('contest-list'))


@require_POST
def logout_view(request):
  if request.user.is_authenticated():
    logout(request)
  messages.info(request, 'You are now logged out.')
  return HttpResponseRedirect(url_reverse('contest-list'))


# TODO: ajax
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
