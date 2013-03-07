from django.db import models

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
  input = models.TextField(blank=True, null=True, default=None)
  output = models.TextField()

  @classmethod
  def get_task(cls, task_id):
    return cls.objects.get(id=task_id)

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
