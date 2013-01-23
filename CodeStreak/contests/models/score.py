from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from CodeStreak.contests.models.task import *
from CodeStreak.contests.models.contest import *

class Score(models.Model):
  SKIPPED = 0.5
  FULL = 1.0

  contest = models.ForeignKey(Contest)
  user = models.ForeignKey(User)
  task = models.ForeignKey(Task)
  score = models.FloatField(default=0)
  # end_time = models.DateTimeField(null=True)
  tries = models.IntegerField(default=0)
  skipped = models.BooleanField(default=False)
  solved = models.BooleanField(default=False)

  @staticmethod
  def _get_entry(contest_id, user_id, task_id):
    return Score.objects.get(
        contest__id=contest_id, 
        user__id=user_id, 
        task__id=task_id,
    )

  @staticmethod
  def _try_task(entry):
    entry.tries += 1
    entry.save()

  @staticmethod
  def solve_task(contest_id, user_id, task_id):
    entry = Score._get_entry(contest_id, user_id, task_id)
    # entry.end_time = datetime.now()
    if entry.skipped == True:
      score = Score.SKIPPED
    else:
      score = Score.FULL
    entry.score = score
    entry.solved = True
    Score._try_task(entry)

  @staticmethod
  def fail_task(contest_id, user_id, task_id):
    entry = Score._get_entry(contest_id, user_id, task_id)
    Score._try_task(entry)

  @staticmethod
  def skip_task(contest_id, user_id, task_id):
    entry = Score._get_entry(contest_id, user_id, task_id)
    entry.skipped = True
    entry.save()

  @staticmethod
  def get_skipped_tasks(contest_id, user_id):
    return Score.objects.filter(
        contest__id=contest_id,
        user__id=user_id,
        skipped=True,
    ).values_list('task__id')

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
