from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
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
  input = models.TextField()
  output = models.TextField()

  @classmethod
  def get_task(cls, task_id):
    return cls.objects.get(id=task_id)

  @classmethod
  def check_output(cls, task_id, output):
    task = cls.get_task(task_id)
    # TODO: mb check for whitespace issues?
    return output.strip() == task.output

  def __unicode__(self):
    return u'Task "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'
    ordering = [
      'difficulty',
      'id',
    ]

__all__ = ['Task']
