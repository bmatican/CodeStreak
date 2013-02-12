from CodeStreak.contests.models.contest import Contest
from CodeStreak.contests.models.task import Task
from CodeStreak.contests.models.score import Score

class InvalidProblemOrderingException:
  pass


class TaskVisibilityHandler:
  def __init__(self, done_task_ids, indexed_task_ids):
    self.done_task_ids = done_task_ids
    self.indexed_task_ids = indexed_task_ids
    self.visible_tasks = []
    self.scores = []
    self.task_by_id = {}
    self.score_by_task_id = {}


  @classmethod
  def from_raw(cls, contest_id, user_id):
    '''
    This will get all the scores for the specific user.
    Also, this will get the task_ordering for the contest.

    This function also sets self.score.
    '''

    scores = Score.get_scores(contest_id, user_id)
    contest = Contest.get_contest(contest_id)
    indexed_task_ids = contest.get_task_ordering()

    done_task_ids = []
    task_by_id = {}
    score_by_task_id = {}

    for s in scores:
      task_by_id[s.task.id] = s.task
      score_by_task_id[s.task.id] = s
      if s.solved or s.skipped:
        done_task_ids.append(s.task.id)

    instance = cls(done_task_ids, indexed_task_ids)
    instance.scores = scores
    instance.task_by_id = task_by_id
    instance.score_by_task_id = score_by_task_id
    instance.visible_tasks = instance.get_visible_tasks()

    return instance

    
  def get_visible_tasks(self):
    if self.visible_tasks != []:
      return self.visible_tasks
    else:
      # no try catch, let
      next = None
      for ind, id in self.indexed_task_ids:
        if ind >= len(self.done_task_ids):
          next = (ind, id) # found it
          break
        if self.done_task_ids[ind] != id:
          raise InvalidProblemOrderingException  # invalid order
      if next == None:
        return self.indexed_task_ids
      else:
        return self.indexed_task_ids[:len(self.done_task_ids) + 1]


  def is_task_visible(self, task_id):
    visible = self.get_visible_tasks()
    return task_id in [id for _, id in visible]


  def is_task_solvable(self, task_id):
    '''
    Can only be called properly if scores are loaded!
    '''

    if self.is_task_visible(task_id):
      score = self.score_by_task_id.get(task_id)
      if score == None or not score.solved:
        # either last one, or just skipped and not solved
        return True
    return False
