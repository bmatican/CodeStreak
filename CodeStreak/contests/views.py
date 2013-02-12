from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse as url_reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from django.utils.timezone import now

import json

from CodeStreak.xhpy import *
from CodeStreak.contests.models import *
from CodeStreak.contests.utils.tasks import *


def contest_decorator(f):
  def wrap(request, contest_id, *args, **kwargs):
    try:
      contest = Contest.get_contest(contest_id, *args, **kwargs)
    except Contest.DoesNotExist:
      raise Http404

    return f(request, contest)
  return wrap


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


def _contest_home_problems_unregistered(request, contest):
  messages.error(request, 'Unimplemented yet...')
  contest_url = url_reverse('contest-home', args=(contest.id,))
  return HttpResponseRedirect(contest_url)


def _contest_home_problems_registered(request, contest, see_all=False):
  user_id = request.user.id
  try:
    handler = TaskVisibilityHandler.from_raw(contest.id, user_id)
  except Score.DoesNotExist:
    raise Http404

  if see_all == True:
    visible_tasks = contest.assigned_tasks.all()
    visible_tasks = [(i, visible_tasks[i].id) \
        for i in xrange(len(visible_tasks))]
  else:
    visible_tasks = handler.get_visible_tasks()


  default_task_id = -1
  task_id_display = int(request.GET.get('task_id', default_task_id))
  if not handler.is_task_visible(task_id_display):
    task_id_display = default_task_id

  content = \
  <div class="contest-problem-set">
    <h2>{'{} Problem Set'.format(contest.name)}</h2>
    <cs:contest-problem-set
      contest={contest}
      ordered_tasks={visible_tasks}
      task_by_id={handler.task_by_id}
      task_id={task_id_display}
      score_by_task_id={handler.score_by_task_id} />
    <script>
      {'var contestId={};'.format(contest.id)}
    </script>
  </div>

  return _contest_home_general(request, contest, content, 'contest-problems')


def _contest_home_problems(request, contest):
  def perror(message):
    messages.error(request, message)

  user = request.user
  is_registered = user.is_authenticated() \
      and contest.is_user_registered(user.id)
  contest_url = url_reverse('contest-home', args=(contest.id,))

  if contest.state == Contest.UNASSIGNED:
    if not user.is_authenticated():
      #TODO: need to flag login somehow...flash button? :)
      perror('You need to login first!')
    elif contest.is_user_registered(user.id):
      #TODO: need to flag registration somehow...flash button? :)
      perror('You need to register first!')
    else:
      perror('Contest has not started yet; problems are not available!')
  elif contest.state == Contest.STARTED:
    if is_registered:
      return _contest_home_problems_registered(request, contest)
    else:
      perror('Contest is underway and you have not registered; ' +
             'problems will be available at the end of the contest!')
  elif contest.state == Contest.PAUSED:
    if is_registered:
      perror('Contest is paused; problems are not available!')
    else:
      #TODO: not really sure what to do here...
      perror('Contest is underway; problems are not available!')
  elif contest.state == Contest.STOPPED:
    if is_registered:
      return _contest_home_problems_registered(request, contest, True)
    else:
      return _contest_home_problems_unregistered(request, contest)
  else:
    perror('Server error...')

  return HttpResponseRedirect(contest_url)


def _contest_home_ranking(request, contest):
  limit = request.GET.get('limit')
  offset = request.GET.get('offset')

  rankings = Participation.get_rankings(contest.id, limit, offset)
  if contest.is_started():
    tasks = contest.assigned_tasks.all()
  else:
    tasks = []

  content = \
  <div class="contest-rankings">
    <h2>{'{} Rankings'.format(contest.name)}</h2>
    <cs:contest-rankings
      contest={contest}
      tasks={tasks}
      rankings={rankings} />
  </div>

  return _contest_home_general(request, contest, content, 'contest-ranking')


def _contest_home_admin(request, contest):
  button = <x:frag />
  show_nothing = False
  if contest.state == Contest.UNASSIGNED:
    if contest.intended_start_date <= now():
      button = <button class="btn btn-success">Start</button>
      button_action = 'contest-start'
    else:
      show_nothing = True
  elif contest.state == Contest.STARTED:
    if contest.get_time_left() > 0.0:
      button = <button class="btn btn-warning">Pause</button>
      button_action = 'contest-pause'
    else:
      button = <button class="btn btn-danger">Stop</button>
      button_action = 'contest-stop'
  elif contest.state == Contest.PAUSED:
    button = <button class="btn btn-success">Resume</button>
    button_action = 'contest-start'
  elif contest.state == Contest.STOPPED:
    show_nothing = True
  else:
    raise Http404 #TODO: just in case of inconsistency...

  if show_nothing == True:
    button_form = <x:frag />
  else:
    button_form = \
    <form class="pull-right" method="post"
      action={url_reverse(button_action, args=(contest.id,))}>
      <cs:csrf request={request} />
      {button}
    </form>

  content = \
  <div class="contest-activity-log">
    {button_form}
    <h2>{'{} Activity Log'.format(contest.name)}</h2>
  </div>

  try:
    entries = LogEntry.get_all_entries(contest.id)
  except:
    raise Http404

  for entry in entries:
    content.appendChild(<cs:log-entry entry={entry} />)

  return _contest_home_general(request, contest, content, 'contest-admin')


def _contest_home_general(request, contest, content, active_tab):
  title = 'CodeStreak - {}'.format(contest.name)
  page = \
  <cs:page request={request} title={title}>
    <cs:header-contest contest={contest} active_tab={active_tab} />
    <cs:content>
      {content}
    </cs:content>
    <cs:footer />
  </cs:page>

  return HttpResponse(str(page))


@contest_decorator
def contest_home(request, contest):
  if not request.user.is_authenticated() \
      or not contest.is_user_registered(request.user.id):
    return _contest_home_ranking(request, contest)
  else:
    if contest.state == Contest.STARTED:
      return _contest_home_problems(request, contest)
    elif contest.state == Contest.UNASSIGNED \
        or contest.state == Contest.STOPPED \
        or contest.state == Contest.PAUSED:
      return _contest_home_ranking(request, contest)
    else:
      raise Http404 #TODO: just in case


@contest_decorator
def contest_problems(request, contest):
  return _contest_home_problems(request, contest)


@contest_decorator
def contest_ranking(request, contest):
  return _contest_home_ranking(request, contest)


@staff_member_required
@contest_decorator
def contest_admin(request, contest):
  if contest.can_user_view_logs(request.user):
    return _contest_home_admin(request, contest)
  else:
    raise Http404 #TODO: this should be useless, due to decorator


@require_POST
@login_required
# Transaction needed in case user registers at the same moment a contest
# starts. Since we have logic which creates db objects based on the set of
# registered users we need to avoid race conditions.
@transaction.commit_on_success
@contest_decorator
def register_to_contest(request, contest):
  contest_url = url_reverse('contest-home', args=(contest.id,))
  try:
    contest.register_user(request.user.id)
    messages.info(request,
        'Registration complete for {}'.format(contest.name))
  except ContestStartedException:
    messages.error(request, 'The contest has already started!')
  except IntegrityError:
    messages.error(request, 'You are already signed up for this contest!')

  return HttpResponseRedirect(contest_url)


@require_POST
@login_required
@transaction.commit_on_success
@contest_decorator
def unregister_from_contest(request, contest):
  contest_url = url_reverse('contest-home', args=(contest.id,))
  try:
    contest.unregister_user(request.user.id)
    messages.info(request,
        'You are no longer registered for {}'.format(contest.name))
  except ContestStartedException:
    messages.error(request, 'The contest has already started!')
  except Participation.DoesNotExist:
    messages.error(request, 'You are not signed up for this contest!')

  return HttpResponseRedirect(contest_url)


@require_POST
@staff_member_required
@transaction.commit_on_success
@contest_decorator
def start_contest(request, contest):
  contest_url = url_reverse('contest-admin', args=(contest.id,))
  try:
    contest.start(request.user.id)
    messages.info(request,
        'Contest {} started'.format(contest.name))
  except ContestStartedException:
    messages.error(request, 'The contest is already started!')

  return HttpResponseRedirect(contest_url)


@require_POST
@staff_member_required
@transaction.commit_on_success
@contest_decorator
def stop_contest(request, contest):
  contest_url = url_reverse('contest-admin', args=(contest.id,))
  try:
    contest.stop(request.user.id)
    messages.info(request,
        'Contest {} stopped'.format(contest.name))
  except ContestNotStartedException:
    messages.error(request, 'The contest is not running!')

  return HttpResponseRedirect(contest_url)


@require_POST
@staff_member_required
@transaction.commit_on_success
@contest_decorator
def pause_contest(request, contest):
  contest_url = url_reverse('contest-admin', args=(contest.id,))
  try:
    contest.pause(request.user.id)
    messages.info(request,
        'Contest {} paused'.format(contest.name))
  except ContestNotStartedException:
    messages.error(request, 'The contest is not running!')

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


def submit_task(user, payload):
  response = {'verdict': 'error'}
  try:
    task_id = payload.get('task_id')
    contest_id = payload.get('contest_id')
    answer = payload.get('answer')

    contest = Contest.get_contest(contest_id)
    if contest.can_user_submit(user.id, task_id):
      great_success = Task.check_output(task_id, answer)

      if great_success:
        Score.solve_task(contest_id, user.id, task_id)
        # add actual state.
        response['verdict'] = 'success'
      else:
        Score.fail_task(contest_id, user.id, task_id)
        response['verdict'] = 'wrong-answer'
      return response
    else:
      return response
  except Contest.DoesNotExist:
    return response


def skip_task(user, payload):
  response = {'verdict': 'error'}
  try:
    task_id = payload.get('task_id')
    contest_id = payload.get('contest_id')

    contest = Contest.get_contest(contest_id)
    if contest.can_user_submit(user.id, task_id):
      Score.skip_task(contest_id, user.id, task_id)
      response['verdict'] = 'skipped'
      return response
    else:
      return response
  except Contest.DoesNotExist:
    return response


data_providers = {
  'skipTask' : skip_task,
  'submitTask' : submit_task,
}


@require_POST
@login_required
def data_provider(request, action):
  global data_providers
  if request.is_ajax():
    payload = json.loads(request.POST.get('payload', ''))
    response = None
    if action in data_providers:
      data_function = data_providers.get(action)
      response = data_function(request.user, payload)
    else:
      return {'verdict': 'error', 'message': 'Unrecognized action'}
    if response == None:
      raise Http404
    else:
      return HttpResponse(json.dumps(response))
  else:
    raise Http404
