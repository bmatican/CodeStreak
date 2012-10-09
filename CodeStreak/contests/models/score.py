from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.task import *

class Score(models.Model):
  user = models.ForeignKey(User)
  task = models.ForeignKey(Task)
  score = models.FloatField()
  elapsed_time = models.FloatField()

  class Meta:
    app_label = 'contests'

__all__ = ['Score']
