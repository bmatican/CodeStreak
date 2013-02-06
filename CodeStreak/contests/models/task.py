from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User

class Task(models.Model):
  CACHE_PREFIX = 'task'

  UNASSIGNED = 0
  EASY = 1
  MEDIUM = 2
  HARD = 3
  DIFFICULTIES = (
    (UNASSIGNED, 'Unassigned'),
    (EASY, 'Easy'),
    (MEDIUM, 'Medium'),
    (HARD, 'Hard'),
  )

  name = models.CharField(max_length=128)
  text = models.TextField()
  difficulty = models.IntegerField(choices=DIFFICULTIES, default=UNASSIGNED)
  input = models.TextField(blank=True, null=True, default=None)
  output = models.TextField()

  @classmethod
  def get_task(cls, task_id):
    cache_key = "{}:{}".format(cls.CACHE_PREFIX, task_id)

    @receiver(post_save, sender=cls, weak=False)
    def fix_cache(sender, **kwargs):
      task = kwargs['instance']
      cache.set(cache_key, task)

    task = cache.get(cache_key)
    if task == None:
      task = cls.objects.get(id=task_id)
      cache.set(cache_key, task)
    return task

  @classmethod
  def check_output(cls, task_id, output):
    task = cls.get_task(task_id)
    return output.strip() == task.output.strip()

  def __unicode__(self):
    return u'Task id: {}, diff: {}'.format(self.id, self.difficulty)

  class Meta:
    app_label = 'contests'
    ordering = [
      'difficulty',
      'id',
    ]

__all__ = ['Task']
