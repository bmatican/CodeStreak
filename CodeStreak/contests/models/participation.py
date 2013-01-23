from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.score import Score

class Participation(models.Model):
  contest = models.ForeignKey(Contest)
  user = models.ForeignKey(User)
  score = models.FloatField(default=0)

  @staticmethod
  def get_entry(contest_id, user_id):
    return Participation.objects.get(
      contest__id=contest_id,
      user__id=user_id
    )

  @staticmethod
  def register_user(contest, user_id):
    user = User.objects.get(id=user_id)
    p = Participation(
      contest=contest,
      user=user,
    )
    p.save()

  @staticmethod
  def solve_full(contest_id, user_id):
    entry = get_entry(contest_id, user_id)
    entry.score = Score.FULL
    entry.save()
    
  @staticmethod
  def solve_skipped(contest_id, user_id):
    entry = get_entry(contest_id, user_id)
    entry.score = Score.FULL
    entry.save()

  def __unicode__(self):
    return u'Participation for contest_id={}, user_id={}'.format(
      self.contest_id, user_id
    )

  class Meta:
    app_label = 'contests'
    unique_together = [
      ['contest', 'user'],
    ]

__all__ = ['Contest']
