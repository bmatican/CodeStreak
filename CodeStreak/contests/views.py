from django.contrib import messages
from django.contrib.auth import logout
from django.core.urlresolvers import reverse as url_reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.timezone import now

import json

from CodeStreak.xhpy import *
from CodeStreak.contests.decorators import *
from CodeStreak.contests.models import *
from CodeStreak.contests.utils.tasks import *


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
  tasks = list(contest.assigned_tasks.all())

  default_task_id = -1
  task_id_display = int(request.GET.get('task_id', default_task_id))
  if not task_id_display in [task.id for task in tasks]:
    task_id_display = default_task_id

  content = \
  <div class="contest-problem-set">
    <h2>{'{} Problem Set'.format(contest.name)}</h2>
    <cs:contest-problem-set
      contest={contest}
      tasks={tasks}
      active_task_id={task_id_display}
    />
    <cs:hidden name={"contest"} value={str(contest.id)} />
  </div>

  return _contest_home_general(request, contest, content, 'contest-problems')


def _contest_home_problems_registered(request, contest, see_all=False):
  user_id = request.user.id
  try:
    handler = TaskVisibilityHandler.from_raw(contest.id, user_id)
  except Score.DoesNotExist:
    raise Http404

  if see_all == True:
    visible_tasks = list(contest.assigned_tasks.all())
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
      tasks={visible_tasks}
      scores={handler.score_by_task_id}
      active_task_id={task_id_display}
    />
    <cs:hidden name={"contest"} value={str(contest.id)} />
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
      return _contest_home_problems_registered(request, contest, False)
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
    <cs:hidden name={"contest"} value = {str(contest.id)} />
  </div>

  return _contest_home_general(request, contest, content, 'contest-ranking')


def _contest_home_admin(request, contest, last_log_entry=None):
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

  if show_nothing == False:
    button.setAttribute('class',
        button.getAttribute('class') + ' js-post-btn')
    button.setAttribute('data-action',
        url_reverse(button_action, args=(contest.id,)))

  entries = LogEntry.get_all_entries(contest.id, last_log_entry)

  new_last_log_entry = 0
  if entries:
    new_last_log_entry = entries[0].id

  content_entries = <div id="log-entries" />
  for entry in entries:
    content_entries.appendChild(<cs:log-entry entry={entry} />)

  content = \
  <div class="contest-activity-log">
    <div class="btn-toolbar pull-right">
      {button}
      <button class="btn js-get-btn"
        data-href={url_reverse('admin:contests_contest_change',
                               args=(contest.id,))}>
        Edit
      </button>
    </div>

    <h2>
      {'{} Activity Log'.format(contest.name)}
    </h2>
    <cs:hidden name={"contest"} value = {str(contest.id)} />
    <cs:hidden name={"lastLogEntry"} value = {str(new_last_log_entry)} />
    {content_entries}
  </div>

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
def contest_admin(request, contest, last_log_entry=None):
  if contest.can_user_view_logs(request.user):
    return _contest_home_admin(request, contest, last_log_entry)
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


@ajax_decorator
@require_POST
@contest_decorator
def submit_task(request, contest, task_id, answer):
  if contest.can_user_submit(request.user.id, task_id):
    great_success = Task.check_output(task_id, answer)

    if great_success:
      Score.solve_task(contest.id, request.user.id, task_id)
      return {'verdict': 'success'}
    else:
      Score.fail_task(contest.id, request.user.id, task_id)
    return {'verdict': 'wrong-answer'}
  else:
    return {'verdict': 'error'}


@ajax_decorator
@require_POST
@contest_decorator
def skip_task(request, contest, task_id):
  if contest.can_user_submit(request.user.id, task_id):
    Score.skip_task(contest.id, request.user.id, task_id)
    return {'verdict': 'skipped'}
  else:
    return {'verdict': 'error'}


@ajax_decorator
@contest_decorator
def get_contest_state(request, contest):
  return {'verdict': 'ok', 'message': contest.state}


@ajax_decorator
@contest_decorator
@staff_member_required
def fetch_contest_logs(request, contest, last_log_entry=0):
  entries = LogEntry.get_all_entries(contest.id, last_log_entry)
  content = <x:frag />
  for entry in entries:
    content.appendChild(<cs:log-entry entry={entry} />)
  all_entries = LogEntry.get_all_entries(contest.id)
  badges = dict()
  for entry in all_entries:
    if not entry.resolved is None:
      badge = \
      <cs:log-entry-resolved-badge entry={entry} />
      badges[entry.id] = str(badge)
  return {
    'verdict': 'ok',
    'message': {
      'entries': str(content),
      'badges': badges,
      'last_log_entry': entries[0].id if entries else last_log_entry
    }
  }

@ajax_decorator
@staff_member_required
@require_POST
def toggle_log(request, log_id):
  try:
    log = LogEntry.get_log_entry(log_id)
  except LogEntry.DoesNotExist:
    raise Http404
  if log.toggle_resolved():
    badge = \
    <cs:log-entry-resolved-badge entry={log} />
    return {
             'verdict': 'ok',
             'badge': str(badge)
           }
  else:
    return {
             'verdict' : 'error',
             'message' : 'This log cannot be toggled.'
           }

data_providers = {
  'skipTask': skip_task,
  'toggleLog' : toggle_log,
  'submitTask': submit_task,
  'getContestState': get_contest_state,
  'fetchContestLogs': fetch_contest_logs,
}


@login_required
def data_provider(request, action):
  if request.is_ajax():
    try:
      payload = json.loads(request.REQUEST.get('payload', '{}'))
    except ValueError:
      response = {'verdict': 'error', 'message': 'Invalid payload'}
      return HttpResponse(json.dumps(response))

    if action in data_providers:
      data_provider = data_providers.get(action)
      try:
        return data_provider(request, **payload)
      except TypeError:
        # Most likely missing or extra payload arguments
        response = {
          'verdict': 'error',
          'message': 'Invalid payload or 500 internal error (TypeError)'
        }
        return HttpResponse(json.dumps(response))
    else:
      response = {'verdict': 'error', 'message': 'Unrecognized action'}
      return HttpResponse(json.dumps(response))
  else:
    raise Http404
