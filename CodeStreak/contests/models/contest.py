from django.db import models, transaction
from django.contrib.auth.models import User

from django.utils.timezone import now
from django.core.cache import cache

from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.log_entry import LogEntry

class Contest(models.Model):
  CACHE_PREFIX = 'contest'
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField()
  end_date = models.DateTimeField()
  paused = models.BooleanField(default=False)
  registered_users = models.ManyToManyField(
      User,
      related_name='registered_contests',
      blank=True,
      through='Participation',
  )
  assigned_tasks = models.ManyToManyField(
      'Task',
      related_name='assigned_contests',
      blank=True
  )

  @classmethod
  def get_all_contests(cls, offset=None, limit=None):
    if offset == None:
      offset = 0
    if limit == None:
      limit = 30
    start = int(offset)
    end = int(offset) + int(limit)
    return cls.objects.all()[start:end]

  @classmethod
  def get_contest(cls, contest_id):
    return cls.objects.get(id=contest_id)

  @classmethod
  def get_task_ordering(cls, contest_id):
    cache_key = cls.CACHE_PREFIX + ":" + str(contest_id)
    tasks = cache.get(cache_key)
    if tasks == None:
      tasks = cls.objects.get(
        id=contest_id
      ).assigned_tasks.values(
        'id'
      )
      tasks = list(enumerate([el['id'] for el in tasks]))
      cache.set(cache_key, tasks)
    return tasks

  def is_user_registered(self, user_id):
    # TODO: hack?
    return (user_id,) in self.registered_users.values_list('id')

  def get_registered_user_count(self):
    return self.registered_users.count()

  def get_assigned_task_count(self):
    return self.assigned_tasks.count()

  def assign_tasks(self, task_ids):
    tasks = Task.objects.filter(id__in=task_ids)
    for t in tasks:
      self.assigned_tasks.add(t)

  def assign_task(self, task_id):
    task = Task.objects.get(id=task_id)
    self.assigned_tasks.add(task)

  @transaction.commit_on_success
  def start(self):
    self.start_date = now()
    self.save()
    LogEntry.start_contest(self.id)

  @transaction.commit_on_success
  def stop(self):
    self.end_date = now()
    self.save()
    LogEntry.stop_contest(self.id)

  @transaction.commit_on_success
  def pause(self):
    self.paused = True
    self.save()
    LogEntry.pause_contest(self.id)

  @transaction.commit_on_success
  def resume(self):
    self.paused = False
    self.save()
    LogEntry.resume_contest(self.id)

  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
