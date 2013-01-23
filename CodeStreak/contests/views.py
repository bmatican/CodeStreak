from django.http import HttpResponse, Http404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import Http404
from django.views.decorators.http import require_POST


import json

from CodeStreak.xhpy import *
from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.participation import Participation

def test(request, test_id=None):
  if test_id == None:
    test_id = 0
  title = 'CodeStreak'

  page = \
  <cs:page title={title}>
    <cs:header />
    <cs:content>
      {'Hi there {}'.format(test_id)}
    </cs:content>
    <cs:footer />
  </cs:page>

  return HttpResponse(str(page))

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
    #return render_to_response('pula/response.html', locals())
  else:
    raise Http404


def contest_list(request):
  limit = request.GET.get('limit')
  offset = request.GET.get('offset')
  contests = Contest.get_all_contests(offset, limit)

  title = 'CodeStreak'

  contest_list = <ul />
  for contest in contests:
    contest_list.appendChild(<li>{contest}</li>)

  page = \
  <cs:page title={title}>
    <cs:header />
    <cs:content>
      {contest_list}
    </cs:content>
    <cs:footer />
  </cs:page>

  return HttpResponse(str(page))


def contest_ranking(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  tasks = contest.assigned_tasks.all()
  users = contest.registered_users.all()

  page = ''
  page += '<p>{}</p>'.format(contest)
  page += '<p>Tasks</p>'
  page += '<ul>'
  for t in tasks:
    page += '<li>{}</li>'.format(t)
  page += '</ul>'

  page += '<p>Users</p>'
  page += '<ul>'
  for u in users:
    page += '<li>{}</li>'.format(u)
  page += '</ul>'

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
