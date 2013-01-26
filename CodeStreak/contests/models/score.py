from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.contest import Contest

class Score(models.Model):
  SKIPPED = 0.5
  FULL = 1.0

  contest = models.ForeignKey(Contest)
  user = models.ForeignKey(User)
  task = models.ForeignKey(Task)
  score = models.FloatField(default=0)
  tries = models.IntegerField(default=0)
  skipped = models.BooleanField(default=False)
  solved = models.BooleanField(default=False)

  @classmethod
  def _get_entry(cls, contest_id, user_id, task_id):
    return cls.objects.get(
        contest__id=contest_id, 
        user__id=user_id, 
        task__id=task_id,
    )

  @classmethod
  def _try_task(cls, entry):
    entry.tries += 1
    entry.save()

  @classmethod
  def solve_task(cls, contest_id, user_id, task_id):
    entry = cls._get_entry(contest_id, user_id, task_id)
    if entry.skipped == True:
      score = cls.SKIPPED
    else:
      score = cls.FULL
    entry.score = score
    entry.solved = True
    cls._try_task(entry)

  @classmethod
  def fail_task(cls, contest_id, user_id, task_id):
    entry = cls._get_entry(contest_id, user_id, task_id)
    cls._try_task(entry)

  @classmethod
  def skip_task(cls, contest_id, user_id, task_id):
    entry = cls._get_entry(contest_id, user_id, task_id)
    entry.skipped = True
    entry.save()

  @classmethod
  def get_scores(cls, contest_id, user_id):
    return cls.objects.select_related(
      'task',
    ).filter(
        contest__id=contest_id,
        user__id=user_id
    ).order_by('task')

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
