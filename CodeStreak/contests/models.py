from django.db import models
from django.contrib.auth.models import User


class Contest(models.Model):
  name = models.CharField(max_length=128)
  start_date = models.DateTimeField()
  end_date = models.DateTimeField()
  registered_users = models.ManyToManyField(User,
                                            related_name='registered_contests')


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
  contest = models.ForeignKey(Contest, blank=True, null=True,
                              on_delete=models.SET_NULL)
  scores = models.ManyToManyField(User, through='Score')


class Score(models.Model):
  user = models.ForeignKey(User)
  task = models.ForeignKey(Task)
  score = models.FloatField()
  elapsed_time = models.FloatField()
