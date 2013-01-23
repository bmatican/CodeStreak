import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404


from CodeStreak.xhpy import *

def test(request, test_id=0):
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

    
