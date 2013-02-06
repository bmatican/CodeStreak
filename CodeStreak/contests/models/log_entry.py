from django.db import models
from django.contrib.auth.models import User

class LogEntry(models.Model):
  CONTEST_STARTED = 1
  CONTEST_PAUSED = 2
  CONTEST_RESUMED = 3
  CONTEST_ENDED = 4
  TASK_PASSED = 5
  TASK_FAILED = 6
  TASK_SKIPPED = 7
  EVENTS = (
    (CONTEST_STARTED, 'Contest started'),
    (CONTEST_PAUSED, 'Contest paused'),
    (CONTEST_RESUMED, 'Contest resumed'),
    (CONTEST_ENDED, 'Contest ended'),
    (TASK_PASSED, 'Task passed'),
    (TASK_FAILED, 'Task failed'),
    (TASK_SKIPPED, 'Task skipped'),
  )

  contest = models.ForeignKey('Contest')
  time = models.DateTimeField(auto_now_add=True)
  type = models.IntegerField(choices=EVENTS)
  user = models.ForeignKey(User, blank=True, null=True,
                           related_name='contest_log_entry_set')
  task = models.ForeignKey('Task', blank=True, null=True)

  @classmethod
  def get_all_entries(cls, contest_id, offset=None, limit=None):
    if offset == None:
      offset = 0
    if limit == None:
      limit = 30
    start = int(offset)
    end = int(offset) + int(limit)
    return cls.objects.all()[start:end]

  @classmethod
  def _make_contest_entry(cls, contest_id, type):
    cls.objects.create(
      contest_id=contest_id,
      type=type,
    ).save()

  @classmethod
  def _make_task_entry(cls, contest_id, type, user_id, task_id):
    cls.objects.create(
      contest_id=contest_id,
      type=type,
      user_id=user_id,
      task_id=task_id,
    ).save()

  @classmethod
  def start_contest(cls, contest_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_STARTED)

  @classmethod
  def end_contest(cls, contest_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_ENDED)

  @classmethod
  def pause_contest(cls, contest_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_PAUSED)

  @classmethod
  def resume_contest(cls, contest_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_RESUMED)

  @classmethod
  def solve_task(cls, contest_id, user_id, task_id):
    cls._make_task_entry(contest_id, cls.TASK_PASSED, user_id, task_id)

  @classmethod
  def skip_task(cls, contest_id, user_id, task_id):
    cls._make_task_entry(contest_id, cls.TASK_SKIPPED, user_id, task_id)

  @classmethod
  def fail_task(cls, contest_id, user_id, task_id):
    cls._make_task_entry(contest_id, cls.TASK_FAILED, user_id, task_id)

  def __unicode__(self):
    if self.user_id != None:
      if self.task_id != None:
        return u'{} -> {} : {} : {}'.format(
          self.time, self.get_type_display(), self.user_id, self.task_id,
        )
      else:
        return u'{} -> {} : {}'.format(
          self.time, self.get_type_display(), self.user_id,
        )
    else:
      return u'{} -> {}'.format(self.time, self.get_type_display())


  class Meta:
    app_label = 'contests'
    ordering = [
      'time',
    ]

__all__ = ['LogEntry']
