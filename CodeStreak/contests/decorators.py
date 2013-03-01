from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

from django.views.decorators.http import require_POST

import json

from CodeStreak.contests.models import Contest



def contest_decorator(f):
  """Decorator which should be used on views expecting a contest object.
  Given a method with request and contest_id as its first two arguments,
  fetches the contest corresponding to contest_id and calls the decorated
  function with request and contest as its first two arguments.
  """
  def wrap(request, contest_id, *args, **kwargs):
    try:
      contest = Contest.get_contest(contest_id)
    except Contest.DoesNotExist:
      raise Http404
    return f(request, contest, *args, **kwargs)
  return wrap

def ajax_decorator(f):
  """Decorator which should be used on AJAX data providers.
  Processes the provider's output, json serializes and wraps it around
  in a HttpResponse if needed.
  """

  def wrap(*args, **kwargs):
    response = f(*args, **kwargs)
    if isinstance(response, HttpResponse):
      return response
    if isinstance(response, dict):
      response = json.dumps(response)
    return HttpResponse(response)
  return wrap
