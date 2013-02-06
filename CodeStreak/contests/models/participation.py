from django.db import models
from django.contrib.auth.models import User

class Participation(models.Model):
  contest = models.ForeignKey('Contest')
  user = models.ForeignKey(User)
  score = models.FloatField(default=0, db_index=True)
  skips_left = models.IntegerField() # should be set from Contest

  def increment_score(self, add_score):
    self.score += add_score
    self.save()

  def skip_task(self):
    self.skips_left -= 1
    self.save()

  @classmethod
  def get_entry(cls, contest_id, user_id):
    return cls.objects.get(
      contest__id=contest_id,
      user__id=user_id
    )

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
