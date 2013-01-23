from django.http import HttpResponse

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
