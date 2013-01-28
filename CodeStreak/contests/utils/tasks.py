from CodeStreak.contests.models.score import Score
from CodeStreak.contests.models.contest import Contest

class InvalidProblemOrderingException:
  pass


class TaskVisibilityHandler:
  def __init__(self, done_task_ids, indexed_task_ids):
    self.done_task_ids = done_task_ids
    self.indexed_task_ids = indexed_task_ids
    self.scores = None


  @classmethod
  def from_raw(cls, contest_id, user_id):
    scores = Score.get_scores(contest_id, user_id)
    indexed_task_ids = Contest.get_task_ordering(contest_id)
    done_task_ids = []
    for s in scores:
      if s.solved or s.skipped:
        done_task_ids.append(s.task.id)
    instance = cls(done_task_ids, indexed_task_ids)
    instance.scores = scores
    return instance

    
  def get_visible_tasks(self):
    # no try catch, let
    next = None
    bla = self.indexed_task_ids
    blaaa = self.done_task_ids
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
