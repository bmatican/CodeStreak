from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User

from django.utils.timezone import now
from django.core.cache import cache

from CodeStreak.contests.models.participation import Participation
from CodeStreak.contests.models.score import Score
from CodeStreak.contests.models.log_entry import LogEntry

class Contest(models.Model):
  CACHE_PREFIX = 'contest'

  UNASSIGNED = 0
  STARTED = 1
  PAUSED = 2
  STOPPED = 3
  STATES = (
    (UNASSIGNED, 'Unassigned'),
    (STARTED, 'Started'),
    (PAUSED, 'Paused'),
    (STOPPED, 'Stopped'),
  )

  name = models.CharField(max_length=128)
  max_skips = models.IntegerField(default=1)
  start_date = models.DateTimeField(blank=True, null=True, default=None)
  end_date = models.DateTimeField(blank=True, null=True, default=None)
  state = models.IntegerField(choices=STATES, default=UNASSIGNED)
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
      contest = cls.get_contest(contest_id)
      tasks = contest.assigned_tasks.values('id')
      tasks = list(enumerate([el['id'] for el in tasks]))
      cache.set(cache_key, tasks)
    return tasks

  def register_user(self, user_id):
    p = Participation(
      contest_id=self.id,
      user_id=user_id,
      skips_left=self.max_skips,
    )
    p.save()

  def unregister_user(self, user_id):
    Participation.get_entry(self.id, user_id).delete()

  def is_user_registered(self, user_id):
    return {'id':user_id} in self.registered_users.values('id')

  def get_registered_user_count(self):
    return self.registered_users.count()

  def get_assigned_task_count(self):
    return self.assigned_tasks.count()

  def _preset_scores(self):
    order = self.get_task_ordering(self.id)
    for u in self.registered_users.all():
      for _, task_id in order:
        Score.create_entry(self.id, u.id, task_id)

  @transaction.commit_on_success
  def start(self):
    if self.state is Contest.UNASSIGNED:
      self.state = Contest.STARTED
      self.start_date = now()
      self.save()
      self._preset_scores()
      LogEntry.start_contest(self.id)
    else:
      raise IntegrityError

  @transaction.commit_on_success
  def stop(self):
    if self.state is Contest.STARTED or self.state is Contest.PAUSED:
      self.state = Contest.STOPPED
      self.end_date = now()
      self.save()
      LogEntry.stop_contest(self.id)
    else:
      raise IntegrityError

  @transaction.commit_on_success
  def pause(self):
    if self.state is Contest.STARTED:
      self.state = Contest.PAUSED
      self.save()
      LogEntry.pause_contest(self.id)
    else:
      raise IntegrityError

  @transaction.commit_on_success
  def resume(self):
    if self.state is Contest.PAUSED:
      self.state = Contest.STARTED
      self.save()
      LogEntry.resume_contest(self.id)
    else:
      raise IntegrityError

  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Contest']
