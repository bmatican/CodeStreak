from django.conf import settings
from django.core.urlresolvers import reverse as url_reverse
from django.utils.formats import date_format
from django.utils.timezone import now

from CodeStreak.xhpy.base import *
from CodeStreak.contests.models import Score, Participation, LogEntry, Contest
from CodeStreak.contests.utils.tasks import InvalidProblemOrderingException


class :cs:header-home(:cs:header):
    def get_prepended_children(self):
        return \
        <cs:header-link link={url_reverse('contest-list')} active={True}>
            Contest List
        </cs:header-link>


class :cs:header-contest(:cs:header):
    attribute object contest @required,
              object request,
              str active_tab = 'contest-problems'

    def get_time_left(self):
        contest = self.getAttribute('contest')
        if contest.state == Contest.STARTED:
            return contest.get_time_left()
        return None

    def get_prepended_children(self):
        contest = self.getAttribute('contest')
        request = self.getAttribute('request')
        user = request.user
        active_tab = self.getAttribute('active_tab')

        if contest.can_user_view_problems(user):
            header_problems = \
            <cs:header-link
                link={url_reverse('contest-problems', args=(contest.id,))}
                active={active_tab == 'contest-problems'}>
                Problems
            </cs:header-link>
        else:
            header_problems = <x:frag />

        header_ranking = \
        <cs:header-link
            link={url_reverse('contest-ranking', args=(contest.id,))}
            active={active_tab == 'contest-ranking'}>
            Rankings
        </cs:header-link>

        prepended_children = \
        <x:frag>
            <cs:header-link
                link={url_reverse('contest-list')}>
                Contest List
            </cs:header-link>
            <cs:header-separator />
            <cs:header-link
                link={url_reverse('contest-home', args=(contest.id,))}
                active={active_tab == 'contest-home'}>
                {contest.name}
            </cs:header-link>
            {header_problems}
            {header_ranking}
        </x:frag>

        if user.is_authenticated() and contest.is_registration_open():
            if contest.is_user_registered(user.id):
                content = 'Unregister'
                link = url_reverse('contest-unregister', args=(contest.id,))
            else:
                content = 'Register'
                link = url_reverse('contest-register', args=(contest.id,))
            prepended_children.appendChild(
                <cs:header-link
                    link={link} post={True}
                    active={active_tab == 'contest-register'}>
                    {content}
                </cs:header-link>)
        if contest.can_user_view_logs(user):
          content = 'Admin'
          link = url_reverse('contest-admin', args=(contest.id,))
          prepended_children.appendChild(
              <cs:header-link
                  link={link}
                  active={active_tab == 'contest-admin'}>
                  {content}
              </cs:header-link>)

        return prepended_children


class :cs:contest-list(:x:element):
    attribute list contests @required
    children empty

    def render(self):
        tbody = <tbody />
        table = \
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th>Contest</th>
                    <th>Start date</th>
                    <th>Duration</th>
                    <th>Registered users</th>
                    <th>Number of tasks</th>
                </tr>
            </thead>
            {tbody}
        </table>

        for contest in self.getAttribute('contests'):
            contest_url = url_reverse('contest-home', args=(contest.id,))
            tbody.appendChild(
                <tr>
                    <td><a href={contest_url}>{contest.name}</a></td>
                    <td>
                        <a href={contest_url}>
                            {date_format(contest.intended_start_date,
                                         'DATETIME_FORMAT')}
                        </a>
                    </td>
                    <td>
                        <a href={contest_url}>
                            {contest.format_intended_duration()}
                        </a>
                    </td>
                    <td>{contest.get_registered_user_count()}</td>
                    <td>{contest.get_assigned_task_count()}</td>
                </tr>)

        return table


class :cs:task-show(:x:element):
    attribute object task @required,
              object score
    children empty

    def render(self):
      task = self.getAttribute('task')
      score = self.getAttribute('score')
      if score == None:
        return self.display_task(task)
      else:
        contest = score.contest
        participation = Participation.get_entry(score.contest_id, score.user_id)

        output_xhp = <x:frag />
        submit_button = <x:frag />
        if score.solved:
          output_xhp = \
          <p class="solved-output">
            <strong>Output</strong><br />
            <code>{task.output}</code>
          </p>
        elif not contest.is_stopped():
          submit_button = \
          <form class="submit-form input-append" data-task-id={task.id}>
            <input class="span2 answer"
              type="text" placeholder="Type answer..." />
            <button class="btn btn-primary submit-button" type="submit"
              data-loading-text="Loading...">
              Submit!
            </button>
          </form>

        skip_button = <x:frag />
        if not contest.is_stopped() and score.can_skip() \
            and participation.skips_left > 0:
          skip_button = \
          <div class="skip-button" data-task-id={task.id}>
            <button class="btn btn-danger">
              Skip task
            </button>
            <span class="help-inline">You can only do it once per contest!</span>
          </div>

        page = \
        <x:frag>
            {output_xhp}
            <div class="task-response" />
            {submit_button}
            {skip_button}
        </x:frag>

        return self.display_task(task, page)

    def display_task(self, task, content=<x:frag />):
        if task.input:
            input_xhp = \
            <p class="input">
                <strong>Input</strong><br />
                <code>{task.input}</code>
            </p>
        else:
            input_xhp = <x:frag />

        page = \
        <div>
            <p><small>{"Difficulty: " + task.get_difficulty_display()}</small></p>
            <strong>Problem</strong>
            <p>{task.text}</p>
            {input_xhp}
            {content}
        </div>
        return page


class :cs:badge(:x:element):
  attribute str content @required,
            str style = "",
            bool badge = True
  children empty

  def render(self):
      style = self.getAttribute("style")
      content = self.getAttribute("content")
      badge = self.getAttribute("badge")

      cls = "badge" if badge else "label"
      if style != "":
        cls = "{0} {0}-{1}".format(cls, style)
      badge = <span class={cls}>{content}</span>
      return badge


class :cs:contest-problem-set(:x:element):
    attribute object contest @required,
              list tasks @required,
              dict scores,
              int active_task_id
    children empty

    def render(self):
        task_content = <div class="tab-content" />
        task_nav = <ul class="nav nav-tabs" />
        display_task_id = self.getAttribute('active_task_id')
        response = \
        <div class="tabbable tabs-left">
          {task_nav}
          {task_content}
        </div>

        tasks = self.getAttribute('tasks')
        score_by_task_id = self.getAttribute('scores')
        if score_by_task_id == None:
            score_by_task_id = {}
        if display_task_id == -1 and len(tasks) > 0:
            display_task_id = tasks[-1].id # focus on the last one...
        for task in tasks:
            score = score_by_task_id.get(task.id)

            badge = \
            <cs:badge
                style={"info"} content={"Untackled"} badge={False}
            />
            if score != None:
                if score.solved:
                    badge = \
                    <cs:badge
                        style={"success"} content={"Solved"} badge={False}
                    />
                elif score.skipped:
                    badge = \
                    <cs:badge
                        style={"warning"} content={"Skipped"} badge={False}
                    />
                elif score.tries != 0:
                    # Wrong answer on previous attempts
                    badge = \
                    <cs:badge
                        style={"important"} content={"Wrong answer"} badge={False}
                    />

            display_name = task.name
            if len(task.name) > 20:
              display_name=task.name[0:18] + '...'

            task_nav.appendChild(
                <li class={'active' if task.id==display_task_id else ''}>
                  <a data-toggle="tab" href={"#task_tab" + str(task.id)}>
                    {badge} {' '}
                    {display_name}
                  </a>
                </li>)
            task_content.appendChild(
                <div id={"task_tab" + str(task.id)}
                     class={"tab-pane active" if task.id==display_task_id else "tab-pane" }>
                    <cs:task-show task={task} score={score} />
                </div>)

        return response


class :cs:contest-rankings(:x:element):
    attribute object contest @required,
              list tasks @required,
              list rankings @required

    def render(self):
        contest = self.getAttribute('contest')
        tasks = self.getAttribute('tasks')
        rankings = self.getAttribute('rankings')

        header_tasks = <x:frag />
        for task in tasks:
            task_url = '{}?task_id={}'.format(
                url_reverse('contest-problems', args=(contest.id,)), task.id)
            header_tasks.appendChild(
                <th class="task-score">
                    <a href={task_url}>
                        {task.name}
                    </a>
                </th>)

        tbody = <tbody />
        table = \
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th>User</th>
                    {header_tasks}
                    <th>Score</th>
                </tr>
            </thead>
            {tbody}
        </table>

        for participation in rankings:
            user = participation.user
            score = participation.score

            task_scores = <x:frag />
            #TODO: we have a way of getting them sorted...this seems duplicate
            scores_per_task = Score.get_scores(contest.id, user.id)
            for task in tasks:
                if len(scores_per_task):
                    if scores_per_task[0].task_id != task.id:
                        raise InvalidProblemOrderingException
                    task_score = scores_per_task[0]
                    scores_per_task = scores_per_task[1:]
                else:
                    task_score = None

                if task_score.solved:
                    content = '{} ({})'.format(task_score.score,
                        task_score.format_tries())
                    xhp = <cs:badge style={"success"} content={content} />
                elif task_score.skipped:
                    xhp = <cs:badge style={"warning"} content={"SK"} />
                elif task_score.tries != 0:
                    content = "WA ({})".format(task_score.format_tries())
                    xhp = \
                    <cs:badge style={"important"} content={content} />
                else:
                    xhp = <cs:badge content={"-"} />
                task_scores.appendChild(<td class="task-score">{xhp}</td>)
            tbody.appendChild(
                <tr>
                    <td><cs:user user={user} /></td>
                    {task_scores}
                    <td>{score}</td>
                </tr>)

        return table


class :cs:log-entry(:x:element):
    attribute LogEntry entry @required

    def render(self):
        entry = self.getAttribute('entry')

        user_information = '-'
        if entry.user:
            user_information = <cs:user user={entry.user} />

        log_information = 'Unexpected log entry type'
        if entry.type == LogEntry.CONTEST_STARTED:
            log_information = 'Started contest'
        elif entry.type == LogEntry.CONTEST_PAUSED:
            log_information = 'Paused contest'
        elif entry.type == LogEntry.CONTEST_RESUMED:
            log_information = 'Resumed contest'
        elif entry.type == LogEntry.CONTEST_ENDED:
            log_information = 'Stopped contest'
        elif entry.type == LogEntry.TASK_PASSED:
            log_information = \
                'Has passed task {} - needs to take a shot'.format(
                    entry.task.name)
        elif entry.type == LogEntry.TASK_FAILED:
            log_information = \
                'Has made an unsuccessful attempt at task {}'.format(
                    entry.task.name)
        elif entry.type == LogEntry.TASK_SKIPPED:
            log_information = \
                'Has skipped task {} - needs to take a shot'.format(
                    entry.task.name)

        return \
        <div class="log-entry row-fluid">
          <div class="span3">
            {date_format(entry.time, 'DATETIME_FORMAT')}
          </div>
          <div class="span2">{user_information}</div>
          <div class="span7">{log_information}</div>
        </div>


__all__ = ["xhpy_cs__header_contest", "xhpy_cs__header_home",
           "xhpy_cs__contest_list", "xhpy_cs__contest_problem_set",
           "xhpy_cs__contest_rankings", "xhpy_cs__task_show",
           "xhpy_cs__log_entry"]
