from django.db import models, transaction, IntegrityError
from django.contrib.auth.models import User
from django.utils.timezone import now

from caching.base import CachingMixin, CachingManager

from CodeStreak.contests.models.participation import Participation
from CodeStreak.contests.models.score import Score
from CodeStreak.contests.models.log_entry import LogEntry


class Contest(CachingMixin, models.Model):
  objects = CachingManager()

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
  max_skips = models.IntegerField(default=1,
      help_text="Maximum number of tasks a participant " +
                "can skip during contest")
  intended_start_date = models.DateTimeField(
      help_text="Intended start date displayed to users")
  intended_duration = models.FloatField(default=3.0,
      help_text="Intended contest duration displayed to users")
  running_time = models.IntegerField(default=0,
      help_text="For internal use: number of seconds contest has run " +
                "in the past")
  last_start_date = models.DateTimeField(blank=True, null=True,
      help_text="For internal use: last time at which contest was " +
                "started")
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

  def get_task_ordering(self):
    return list(enumerate([el['id'] for el in \
        self.assigned_tasks.values('id')]))

  def register_user(self, user_id):
    if self.state == Contest.UNASSIGNED:
      p = Participation(
        contest_id=self.id,
        user_id=user_id,
        skips_left=self.max_skips,
      )
      p.save()
    else:
      raise ContestStartedException(self)

  def unregister_user(self, user_id):
    if self.state == Contest.UNASSIGNED:
      Participation.get_entry(self.id, user_id).delete()
    else:
      raise ContestStartedException(self)

  def is_user_registered(self, user_id):
    return {'id': user_id} in self.registered_users.values('id')

  def is_registration_open(self):
    return self.state == Contest.UNASSIGNED

  def is_started(self):
    return self.state != Contest.UNASSIGNED

  def is_stopped(self):
    return self.state == Contest.STOPPED

  def get_registered_user_count(self):
    return self.registered_users.count()

  def get_assigned_task_count(self):
    return self.assigned_tasks.count()

  def _preset_scores(self):
    order = self.get_task_ordering()
    for u in self.registered_users.all():
      for _, task_id in order:
        Score.create_entry(self.id, u.id, task_id)

  @transaction.commit_on_success
  def start(self, admin_user_id=None):
    if self.state is Contest.UNASSIGNED:
      self.state = Contest.STARTED
      self.last_start_date = now()
      self.save()
      self._preset_scores()
      LogEntry.start_contest(self.id, admin_user_id)
    elif self.state is Contest.PAUSED:
      self.resume(admin_user_id)
    else:
      raise ContestStartedException

  @transaction.commit_on_success
  def stop(self, admin_user_id=None):
    if self.state is Contest.STARTED or self.state is Contest.PAUSED:
      self.state = Contest.STOPPED
      self.save()
      LogEntry.stop_contest(self.id, admin_user_id)
    else:
      raise ContestNotStartedException

  @transaction.commit_on_success
  def pause(self, admin_user_id=None):
    if self.state is Contest.STARTED:
      self.state = Contest.PAUSED
      self.running_time = self.get_current_running_time()
      self.save()
      LogEntry.pause_contest(self.id, admin_user_id)
    else:
      raise ContestNotStartedException

  @transaction.commit_on_success
  def resume(self, admin_user_id=None):
    if self.state is Contest.PAUSED:
      self.state = Contest.STARTED
      self.save()
      LogEntry.resume_contest(self.id, admin_user_id)
    else:
      raise ContestStartedException

  def get_current_running_time(self):
    if self.state == Contest.UNASSIGNED:
      return 0.0
    elif self.state == Contest.STARTED:
      return self.running_time + (now() - self.last_start_date).total_seconds()
    else:
      return self.running_time

  def get_time_left(self):
      return max(0.0, self.intended_duration * 60 * 60 -
                      self.get_current_running_time())

  def can_user_submit(self, user_id, task_id):
    if self.state != Contest.STARTED:
      return False

    is_registered = self.is_user_registered(user_id)
    if not is_registered:
      return False

    from CodeStreak.contests.utils.tasks import TaskVisibilityHandler
    handler = TaskVisibilityHandler.from_raw(self.id, user_id)
    return handler.is_task_solvable(task_id)

  def can_user_view_problems(self, user):
    return self.is_started()

  def can_user_view_logs(self, user):
    return user.is_staff

  def format_intended_duration(self):
    return '{} {}'.format(
        self.intended_duration,
        'hour' if self.intended_duration == 1 else 'hours')

  def __unicode__(self):
    return u'Contest "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'


class ContestStartedException(Exception):
  pass


class ContestNotStartedException(Exception):
  pass


__all__ = ['Contest', 'ContestStartedException', 'ContestNotStartedException']
