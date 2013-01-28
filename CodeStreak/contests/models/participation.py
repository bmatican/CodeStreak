from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.score import Score

class Participation(models.Model):
  contest = models.ForeignKey(Contest)
  user = models.ForeignKey(User)
  score = models.FloatField(default=0, db_index=True)

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

  @classmethod
  def update_score(cls, contest_id, user_id, add_score):
    entry = cls.get_entry(contest_id, user_id)
    entry.score += add_score
    entry.save()

  @classmethod
  def get_rankings(cls, contest_id, limit=None, offset=None):
    if offset == None:
      offset = 0
    if limit == None:
      limit = 30
    end = int(offset) + int(limit)

    return cls.objects.select_related(
        'user',
    ).filter(
        contest__id=contest_id,
    ).order_by('-score')[offset:end]

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
