from django.db import models
from django.contrib.auth.models import User
from time import time

from CodeStreak.contests.models.task import *

class Contest(models.Model):
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField(null=True, blank=True, default=None)
  end_date = models.DateTimeField(null=True, blank=True, default=None)
  registered_users = models.ManyToManyField(
      User,
      related_name='registered_contests',
  )
  assigned_tasks = models.ManyToManyField(
      Task,
      related_name='assigned_contests',
  )

  @staticmethod
  def get_contest(contest_id):
    return Contest.objects.get(id=contest_id)

  @staticmethod
  def assign_tasks(contest_id, task_ids):
    tasks = Task.objects.filter(id__in=task_ids)
    contest = Contest.get_contest(contest_id)
    for t in tasks:
      contest.assigned_tasks.add(t)

  @staticmethod
  def assign_task(contest_id, task_id):
    task = Task.objects.get(id=task_id)
    Contest.get_contest(contest_id).assigned_tasks.add(task)

  @staticmethod
  def register_user(contest_id, user_id):
    user = User.objects.get(id=user_id)
    Contest.get_contest(contest_id).registered_users.add(user)

  @staticmethod
  def start_contest(contest_id):
    contest = Contest.get_contest(contest_id)
    contest.start_date = time()    
    contest.save()
    # TODO: admin, start for all users on all terminals, from controller

  @staticmethod
  def stop_contest(contest_id):
    contest = Contest.get_contest(contest_id)
    contest.end_date = time()    
    contest.save()
    # TODO: admin, stop for all users on all terminals, from controller


  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
