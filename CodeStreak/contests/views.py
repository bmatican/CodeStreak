import json

from django.http import HttpResponse
from django.shortcuts import render_to_response

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

def pula(request):
  if request.is_ajax() and request.method == 'POST':
    test = request.POST.get('test', '')
    response = {
      'test' : test
    }
    return HttpResponse(json.dumps(response))
    #return render_to_response('pula/response.html', locals())
  else:
    pass # should render 404
    
