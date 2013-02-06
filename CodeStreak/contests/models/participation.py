from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User

class Participation(models.Model):
  CACHE_PREFIX = 'participation'

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
    cache_key = "{}:{}:{}".format(cls.CACHE_PREFIX, contest_id, user_id)

    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      participation = kwargs['instance']
      cache.set(cache_key, participation)

    participation = cache.get(cache_key)
    if participation == None:
      participation = cls.objects.get(
        contest__id=contest_id,
        user__id=user_id
      )
      cache.set(cache_key, participation)
    return participation

  @classmethod
  def get_rankings(cls, contest_id, limit=None, offset=None):
    #TODO: need to think about how to cache limit/offset nicely...
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
