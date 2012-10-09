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

  @staticmethod
  def get_task(task_id):
    return Task.objects.get(id=task_id)

  @staticmethod
  def check_output(task_id, output):
    task = Task.get_task(task_id)
    # TODO: mb check for whitespace issues?
    ret = (output == task.output)
    return ret

  def __unicode__(self):
    return u'Task "{0}"'.format(self.name)

  class Meta:
    app_label = 'contests'

__all__ = ['Task']
