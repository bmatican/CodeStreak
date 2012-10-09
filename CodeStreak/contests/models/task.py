from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.contest import *

class Task(models.Model):
  UNASSIGNED = 0
  EASY = 1
  MEDIUM = 2
  HARD = 3
  DIFFICULTIES = (
    (UNASSIGNED, 'Unassigned'),
    (EASY, 'Easy'),
    (MEDIUM, 'Medium'),
    (HARD, 'Hard'),
  )

  name = models.CharField(max_length=128)
  text = models.TextField()
  difficulty = models.IntegerField(choices=DIFFICULTIES, default=UNASSIGNED)
  input = models.TextField()
  output = models.TextField()
  contest = models.ForeignKey(Contest, blank=True, null=True,
                              on_delete=models.SET_NULL)
  scores = models.ManyToManyField(User, through='Score')

  def __unicode__(self):
    return u'Task "%s"' % self.name

  class Meta:
    app_label = 'contests'

__all__ = ['Task']
