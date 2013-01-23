from django.db import models
from django.contrib.auth.models import User
from time import time

from CodeStreak.contests.models.task import Task

class Contest(models.Model):
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField(null=True, blank=True, default=None)
  end_date = models.DateTimeField(null=True, blank=True, default=None)
  registered_users = models.ManyToManyField(
      User,
      related_name='registered_contests',
      through='Participation',
  )
  assigned_tasks = models.ManyToManyField(
      Task,
      related_name='assigned_contests',
  )

  def get_registered_user_count(self):
    return self.registered_users.count()

  def get_assigned_task_count(self):
    return self.assigned_tasks.count()

  @staticmethod
  def get_all_contests(offset=None, limit=None):
    if offset == None:
      offset = 0
    if limit == None:
      limit = 30
    end = int(offset) + int(limit)
    return Contest.objects.all()[offset:end]

  @staticmethod
  def get_contest(contest_id):
    return Contest.objects.get(id=contest_id)

  @staticmethod
  def assign_tasks(contest, task_ids):
    tasks = Task.objects.filter(id__in=task_ids)
    for t in tasks:
      contest.assigned_tasks.add(t)

  @staticmethod
  def assign_task(contest, task_id):
    task = Task.objects.get(id=task_id)
    contest.assigned_tasks.add(task)

  @staticmethod
  def start_contest(contest):
    contest.start_date = time()
    contest.save()
    # TODO: admin, start for all users on all terminals, from controller

  @staticmethod
  def stop_contest(contest):
    contest.end_date = time()
    contest.save()
    # TODO: admin, stop for all users on all terminals, from controller

  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
