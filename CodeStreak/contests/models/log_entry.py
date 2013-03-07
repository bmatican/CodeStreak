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
  # null if not applicable
  resolved = models.NullBooleanField()
  task = models.ForeignKey('Task', blank=True, null=True)

  def toggle_resolved(self):
    if self.resolved == None:
      return False
    else:
      self.resolved = not self.resolved
      self.save()
      return True

  @classmethod
  def get_log_entry(cls, log_id):
    return cls.objects.get(id=log_id)

  @classmethod
  def get_all_entries(cls, contest_id, last_log_entry=None):
    query = cls.objects.select_related(
      'user'
    ).filter(contest__id=contest_id)
    if last_log_entry:
      query = query.filter(id__gt=last_log_entry)
    return query.all()

  @classmethod
  def _make_contest_entry(cls, contest_id, type, user_id):
    cls.objects.create(
      contest_id=contest_id,
      type=type,
      user_id=user_id,
    ).save()

  @classmethod
  def get_default_resolved(cls, type):
    if type == LogEntry.TASK_PASSED or type == LogEntry.TASK_SKIPPED:
      return False
    else:
      return None

  @classmethod
  def _make_task_entry(cls, contest_id, type, user_id, task_id):
    default_resolved_value = cls.get_default_resolved(type)
    cls.objects.create(
      contest_id=contest_id,
      type=type,
      user_id=user_id,
      task_id=task_id,
      resolved = default_resolved_value
    ).save()

  @classmethod
  def start_contest(cls, contest_id, user_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_STARTED, user_id)

  @classmethod
  def stop_contest(cls, contest_id, user_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_ENDED, user_id)

  @classmethod
  def pause_contest(cls, contest_id, user_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_PAUSED, user_id)

  @classmethod
  def resume_contest(cls, contest_id, user_id):
    cls._make_contest_entry(contest_id, cls.CONTEST_RESUMED, user_id)

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
    ordering = ('-time',)
    verbose_name_plural = 'log entries'

__all__ = ['LogEntry']
