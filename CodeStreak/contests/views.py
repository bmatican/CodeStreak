from django.http import HttpResponse, Http404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.http import Http404


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

    
def display_contest(request, contest_id=None):
  if contest_id == None:
    return _display_all_contests(request)
  else:
    return _display_contest(request, contest_id)

def _display_all_contests(request):
  limit = request.GET.get('limit')
  offset = request.GET.get('offset')
  contests = Contest.get_all_contests(offset, limit)
  page = ''
  page += '<ul>'
  for c in contests:
    page += '<li>{}</li>'.format(c)
  page += '</ul>'
  return HttpResponse(str(page))

def _display_contest(request, contest_id):
  try:
    contest = Contest.get_contest(contest_id)
  except Contest.DoesNotExist:
    raise Http404

  tasks = Contest.get_assigned_tasks(contest)
  users = Contest.get_registered_users(contest)

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

def register_to_contest(request, contest_id, user_id):
  try:
    contest = Contest.get_contest(contest_id)
    Participation.register_user(contest, user_id)
  except Contest.DoesNotExist:
    raise Http404
  except User.DoesNotExist:
    raise Http404
  except IntegrityError:
    return HttpResponse("You are already signed up for this contest!")

  page = ''
  page += '<p>Registration complete for {}</p>'.format(contest)
  return HttpResponse(str(page))
