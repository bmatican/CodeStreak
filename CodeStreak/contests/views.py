from django.http import HttpResponse

def test(request, test_id=0):
  return HttpResponse('Hi there {}'.format(test_id))
