from django.db import models
from django.contrib.auth.models import User

from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.task import Task

class LogEntry(models.Model):
  CONTEST_STARTED = 1
  CONTEST_PAUSED = 2
  CONTEST_ENDED = 3
  TASK_PASSED = 4
  TASK_FAILED = 5
  TASK_SKIPPED = 6
  EVENTS = (
    (CONTEST_STARTED, 'Contest started'),
    (CONTEST_PAUSED, 'Contest paused'),
    (CONTEST_ENDED, 'Contest ended'),
    (TASK_PASSED, 'Task passed'),
    (TASK_FAILED, 'Task failed'),
    (TASK_SKIPPED, 'Task skipped'),
  )

  contest = models.ForeignKey(Contest)
  time = models.DateTimeField(auto_now_add=True)
  type = models.IntegerField(choices=EVENTS)
  user = models.ForeignKey(User, blank=True, null=True,
                           related_name='contest_log_entry_set')
  task = models.ForeignKey(Task, blank=True, null=True)

  class Meta:
    app_label = 'contests'

__all__ = ['LogEntry']
