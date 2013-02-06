from django.db import models, transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils.timezone import now

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
    cache_key = "{}:{}".format(cls.CACHE_PREFIX, contest_id)

    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      contest = kwargs['instance']
      cache.set(cache_key, contest)

    contest = cache.get(cache_key)
    if contest == None:
      contest = cls.objects.get(id=contest_id)
      cache.set(cache_key, contest)
    return contest

  @classmethod
  def get_task_ordering(cls, contest_id):
    cache_key = "{}:{}/task_ordering".format(cls.CACHE_PREFIX, contest_id)

    def get_and_sort_tasks(contest):
      return list(enumerate([el['id'] for el in \
          contest.assigned_tasks.values('id')]))

    """
    # this is not really needed, as you should never call get_task_ordering
    # without the contest having started...and you should never change problem
    # ordering mid contest...
    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      contest = kwargs['instance']
      tasks = get_and_sort_tasks(contest)
      cache.set(cache_key, tasks)
    """

    tasks = cache.get(cache_key)
    if tasks == None:
      tasks = get_and_sort_tasks(cls.get_contest(contest_id))
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
