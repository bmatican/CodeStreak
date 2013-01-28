from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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


# TODO: Display all tasks if contest is over.
@login_required
def contest_home(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  task_id_display = request.GET.get('task_id', -1)

  title = 'CodeStreak - {}'.format(contest.name)
  content = <div class="contest-problem-set" />
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab="contest-home" />
    <cs:content>
      <h2>{'{} Problem Set'.format(contest.name)}</h2>
      {content}
      <script>
        {'var contestId=' + contest_id + ";"}
      </script>
    </cs:content>
    <cs:footer />
  </cs:page>

  user_id = request.user.id
  try:
    handler = TaskVisibilityHandler.from_raw(contest_id, user_id)
    scores = handler.scores
  except Score.DoesNotExist:
    raise Http404
  except Contest.DoesNotExist:
    raise Http404

  task_by_id = {}
  score_by_task_id = {}
  for score in scores:
    task_by_id[score.task.id] = score.task
    score_by_task_id[score.task.id] = score

  ordered_tasks = handler.get_visible_tasks()
  if len(ordered_tasks) > 0:
    _, task_id = ordered_tasks[-1]
    if task_id not in task_by_id:
      task_by_id[task_id] = Task.get_task(task_id)

  content.appendChild(
      <cs:contest-problem-set
        contest={contest}
        ordered_tasks={ordered_tasks}
        task_by_id={task_by_id}
        task_id={task_id_display}
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
  content = <div class="contest-rankings" />
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


def isOperationAllowed(contest_id, task_id, user_id):
  try:
    contest = Contest.get_contest(contest_id)
    if contest.is_user_registered(user_id):
      # check if task visible
      return True
    else:
      return False
  except Contest.DoesNotExist:
    return False


def submitTask(user, payload):
  try:
    task_id = payload.get('task_id')
    contest_id = payload.get('contest_id')
    answer = payload.get('answer')

    #FIXME: check if operation allowed    

    great_success = Task.check_output(task_id, answer)

    response = None
    if (great_success):
      Score.solve_task(contest_id, user.id, task_id)
      # add actual state.
      response = {
                   'verdict' : 'success'
                 }
    else:
      Score.fail_task(contest_id, user.id, task_id)
      response = {
                   'verdict' : 'wrong-answer'
                 }
    return response
  except:
    return {}

def skipTask(user, payload):
  try:
    task_id = payload.get('task_id')
    contest_id = payload.get('contest_id')

    #FIXME: check if operation allowed.

    Score.skip_task(contest_id, user.id, task_id)
    
    return {
             'verdict' : 'skipped'
           }
  except:
    return {}

data_providers = {
  'skipTask' : skipTask,
  'submitTask' : submitTask,
}

@require_POST
@login_required
def data_provider(request, action):
  print 'here'
  global data_providers
  if request.is_ajax():
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


@login_required
@staff_member_required
def logs(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  title = 'CodeStreak - {} activity log'.format(contest.name)

  content = <div class="contest-activity-log" />
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab="contest-logs" />
    <cs:content>
      <h2>{'{} Activity Log'.format(contest.name)}</h2>
      {content}
    </cs:content>
    <cs:footer />
  </cs:page>

  try:
    entries = LogEntry.get_all_entries(contest_id)
  except:
    raise Http404

  for entry in entries:
    content.appendChild(<cs:log-entry entry={entry} />)

  return HttpResponse(str(page))
