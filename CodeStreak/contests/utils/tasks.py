class InvalidProblemOrderingException:
  pass


class TaskVisibilityHandler:
  def __init__(self, seen_ids, indexed_task_ids):
    self.seen_ids = seen_ids
    self.indexed_task_ids = indexed_task_ids


  def get_current_task(self):
    for ind, id in self.indexed_task_ids:
      if ind >= len(self.seen_ids):
        return (ind, id) # found it
      test = self.seen_ids[ind]
      if self.seen_ids[ind] != id:
        raise InvalidProblemOrderingException  # invalid order
    return None   # no next problem


  def get_visible_tasks(self):
    # no try catch, let
    next = self.get_current_task()
    if next == None:
      return self.indexed_task_ids
    else:
      return self.indexed_task_ids[:len(self.seen_ids) + 1]


  def is_task_visible(self, task_id):
    visible = self.get_visible_tasks()
    return task_id in [id for _, id in visible]
