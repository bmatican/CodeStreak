from django.db import models, transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User
from datetime import datetime

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.log_entry import LogEntry
from CodeStreak.contests.models.participation import Participation

class Score(models.Model):
  CACHE_PREFIX = 'score'

  SKIPPED = 0.5
  FULL = 1.0

  contest = models.ForeignKey('Contest')
  user = models.ForeignKey(User)
  task = models.ForeignKey('Task')
  score = models.FloatField(default=0)
  tries = models.IntegerField(default=0)
  skipped = models.BooleanField(default=False)
  solved = models.BooleanField(default=False)

  @classmethod
  def _make_args(cls, contest_id, user_id, task_id):
    return {
      'contest_id' : contest_id,
      'user_id' : user_id,
      'task_id' : task_id,
    }

  @classmethod
  def get_entry(cls, contest_id, user_id, task_id):
    cache_key = "{}:{}:{}:{}".format(cls.CACHE_PREFIX, contest_id, user_id, task_id)

    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      score = kwargs['instance']
      cache.set(cache_key, score)

    score = cache.get(cache_key)
    if score == None:
      args = cls._make_args(contest_id, user_id, task_id)
      score = cls.objects.get(**args)
      cache.set(cache_key, score)
    return score

  @classmethod
  def create_entry(cls, contest_id, user_id, task_id):
    args = cls._make_args(contest_id, user_id, task_id)
    cls.objects.create(**args)

  def _try_task(self):
    self.tries += 1
    self.save()

  @classmethod
  @transaction.commit_on_success
  def solve_task(cls, contest_id, user_id, task_id):
    entry = cls.get_entry(contest_id, user_id, task_id)
    if not entry.solved:
      if entry.skipped == True:
        score = cls.SKIPPED
      else:
        score = cls.FULL
      entry.score = score
      entry.solved = True
      entry._try_task()
      p = Participation.get_entry(contest_id, user_id)
      p.increment_score(score)
      LogEntry.solve_task(contest_id, user_id, task_id)
    else:
      raise IntegrityError

  @classmethod
  @transaction.commit_on_success
  def fail_task(cls, contest_id, user_id, task_id):
    entry = cls.get_entry(contest_id, user_id, task_id)
    entry._try_task()
    LogEntry.fail_task(contest_id, user_id, task_id)

  @classmethod
  @transaction.commit_on_success
  def skip_task(cls, contest_id, user_id, task_id):
    entry = cls.get_entry(contest_id, user_id, task_id)
    p = Participation.get_entry(contest_id, user_id)
    can_skip = not entry.skipped and not entry.solved and p.skips_left > 0
    if can_skip:
      entry.skipped = True
      entry.save()
      p.skip_task()
      LogEntry.skip_task(contest_id, user_id, task_id)
    else:
      raise IntegrityError

  @classmethod
  def get_scores(cls, contest_id, user_id, with_tasks=True):
    cache_key = "{}:{}:{}:{}".format(cls.CACHE_PREFIX, contest_id, user_id, 'tasks' if with_tasks else 'no_tasks')

    """
    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      score = kwargs['instance']
      cache.set(cache_key, score)
    """

    scores = cache.get(cache_key)
    if scores == None:
      scores = cls.objects.filter(
          contest__id=contest_id,
          user__id=user_id
      ).order_by('task')
      if with_tasks:
        scores = scores.select_related(
            'task',
        )
      cache.set(cache_key, scores.all())
    return scores.all()

  def format_tries(self):
    return '{} {}'.format(
        self.tries,
        'try' if self.tries == 1 else 'tries')

  def __unicode__(self):
    return u'Score for contest_id={0}, user_id={1}, task_id={2}'.format(
        self.contest_id, self.user_id, self.task_id
    )

  class Meta:
    app_label = 'contests'
    unique_together = [
      ['contest', 'user', 'task']
    ]

__all__ = ['Score']
