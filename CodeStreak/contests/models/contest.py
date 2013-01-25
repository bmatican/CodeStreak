from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from CodeStreak.contests.models.task import Task

class Contest(models.Model):
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField(null=True, blank=True, default=None)
  end_date = models.DateTimeField(null=True, blank=True, default=None)
  paused = models.BooleanField(default=False)
  registered_users = models.ManyToManyField(
      User,
      related_name='registered_contests',
      blank=True,
      through='Participation',
  )
  assigned_tasks = models.ManyToManyField(
      Task,
      related_name='assigned_contests',
      blank=True
  )

  @classmethod
  def get_all_contests(cls, offset=None, limit=None):
    if offset == None:
      offset = 0
    if limit == None:
      limit = 30
    end = int(offset) + int(limit)
    return cls.objects.all()[offset:end]

  @classmethod
  def get_contest(cls, contest_id):
    return cls.objects.get(id=contest_id)

  @classmethod
  def get_task_ordering(cls, contest_id):
    cached = False
    if cached:
      tasks = []
    else:
      tasks = cls.objects.get(
        id=contest_id
      ).assigned_tasks.values(
        'id'
      )
      tasks = [el['id'] for el in tasks]
    return list(enumerate(tasks))

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

  def start(self):
    self.start_date = now()
    self.save()

  def stop(self):
    self.end_date = now()
    self.save()

  def pause(self):
    self.paused = True
    self.save()

  def resume(self):
    self.paused = False
    self.save()

  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
