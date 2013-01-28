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
def view_task(request, task_id):
  try:
    task = Task.get_task(task_id)
  except Task.DoesNotExist:
    raise Http404

  title = 'CodeStreak - {}'.format(task.name)
  content = <x:frag />
  page = \
  <cs:page request={request} title={title}>
    <cs:header />
    <cs:content>
      <cs:task-show task={task} />
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
  content = <div />
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
    scores = Score.get_scores(contest_id, user_id)
    indexed_task_ids = Contest.get_task_ordering(contest_id)
  except Score.DoesNotExist:
    raise Http404
  except Contest.DoesNotExist:
    raise Http404

  done_task_ids = []
  task_by_id = {}
  score_by_task_id = {}
  for score in scores:
    task_by_id[score.task.id] = score.task
    score_by_task_id[score.task.id] = score
    if score.solved or score.skipped:
        done_task_ids.append(score.task.id)

  handler = TaskVisibilityHandler(done_task_ids, indexed_task_ids)
  ordered_tasks = handler.get_visible_tasks()
  for p, task_id in ordered_tasks:
    if task_id not in task_by_id:
      # Should only ever happen once, for the next task the user needs
      # to attempt
      task_by_id[task_id] = Task.get_task(task_id)

  content.appendChild(
      <cs:contest-problem-set
        contest={contest}
        ordered_tasks={ordered_tasks}
        task_by_id={task_by_id}
        score_by_task_id={score_by_task_id} />)

  return HttpResponse(str(page))


def contest_ranking(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404
  limit = request.GET.get('limit')
  offset = request.GET.get('offset')

  title = 'CodeStreak - {}'.format(contest.name)
  content = <div />
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab="contest-ranking" />
    <cs:content>
      <h2>{'{} Ranking'.format(contest.name)}</h2>
      {content}
    </cs:content>
    <cs:footer />
  </cs:page>

  rankings = Participation.get_rankings(contest.id, limit, offset)
  content.appendChild(
      <cs:contest-rankings
        contest={contest}
        tasks={contest.assigned_tasks.all()}
        rankings={rankings} />)

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


def getScores(user, payload):
  return {
            'scores' : 'scores',
         }

def submitTask(user, payload):
  return {
            'verdict'   : 'success'
         }

data_providers = {
  'getScores' : getScores,
  'submitTask' : submitTask,
}

def data_provider(request, action):
  print 'here'
  global data_providers
  if request.is_ajax() and request.method == 'POST':
    payload = json.loads(request.POST.get('payload', ''))
    response = None
    if action in data_providers:
      data_function = data_providers.get(action)
      response = data_function(request.user, payload)
    else:
      print 'Unrecognized action'
    if response == None:
      raise Http404
    else:
      return HttpResponse(json.dumps(response))
  else:
    raise Http404
