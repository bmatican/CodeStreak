from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.score import Score

class Participation(models.Model):
  contest = models.ForeignKey(Contest)
  user = models.ForeignKey(User)
  score = models.FloatField(default=0)

  @classmethod
  def get_entry(cls, contest_id, user_id):
    return cls.objects.get(
      contest__id=contest_id,
      user__id=user_id
    )

  @classmethod
  def register_user(cls, contest_id, user_id):
    p = cls(
      contest_id=contest_id,
      user_id=user_id,
    )
    p.save()

  @classmethod
  def unregister_user(cls, contest_id, user_id):
    cls.get_entry(contest_id, user_id).delete()

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
      self.contest_id, self.user_id
    )

  class Meta:
    app_label = 'contests'
    unique_together = [
      ['contest', 'user'],
    ]

__all__ = ['Participation']
