from django.db import models
from django.contrib.auth.models import User

class Contest(models.Model):
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField()
  end_date = models.DateTimeField()
  registered_users = models.ManyToManyField(User,
                                            related_name='registered_contests')

  def __unicode__(self):
    return u'Contest "%s"' % self.name

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
