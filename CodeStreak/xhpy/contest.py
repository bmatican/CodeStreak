from django.conf import settings
from django.core.urlresolvers import reverse as url_reverse
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
            <cs:header-link
                link={url_reverse('contest-users', args=(contest.id,))}
                active={active_tab == 'contest-users'}>
                Registered users
            </cs:header-link>
            <cs:header-link
                link={url_reverse('contest-problems', args=(contest.id,))}
                active={active_tab == 'contest-problems'}>
                Problems
            </cs:header-link>
            <cs:header-link
                link={url_reverse('contest-ranking', args=(contest.id,))}
                active={active_tab == 'contest-ranking'}>
                Rankings
            </cs:header-link>
        </x:frag>
        if user.is_authenticated() and contest.state == Contest.UNASSIGNED:
            if contest.is_user_registered(user.id):
                content = 'Unregister'
                link = url_reverse('contest-unregister', args=(contest.id,))
            else:
                content = 'Register'
                link = url_reverse('contest-register', args=(contest.id,))
            prepended_children.appendChild(
                <cs:header-link
                    link={link}
                    active={active_tab == 'contest-register'}>
                    {content}
                </cs:header-link>)
        if user.is_staff:
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
                            {contest.intended_start_date}
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
              object score @required
    children empty

    def render(self):
      task = self.getAttribute('task')
      score = self.getAttribute('score')
      participation = Participation.get_entry(score.contest_id, score.user_id)

      if task.input:
        input_xhp = \
        <p class="input">
          <strong>Input</strong><br />
          <code>{task.input}</code>
        </p>
      else:
        input_xhp = <x:frag />

      if score.solved:
        output_xhp = \
        <p class="solved-output">
          <strong>Output</strong><br />
          <code>{task.output}</code>
        </p>
        submit_button = <x:frag />
      else:
        output_xhp = <x:frag />
        submit_button = \
        <div class="input-append">
          <input class="span2" id={"taskanswer"+str(task.id)}
            type="text" placeholder="Type answer..." />
          <button class="btn btn-primary" type="button"
            id={"answerbutton" + str(task.id)}
            onClick={"submitTask(" +str(task.id) + ")"}
            data-loading-text="Loading...">
            Submit!
          </button>
        </div>

      if score.can_skip() and participation.skips_left > 0:
        skip_button = \
        <div>
          <button class="btn btn-danger"
            onclick={"skipTask(" + str(task.id) + ")"}>
            Skip task
          </button>
          <span class="help-inline">You can only do it once per contest!</span>
        </div>
      else:
        skip_button = <x:frag />

      page = \
      <div>
        <p><small>{"Difficulty: " + task.get_difficulty_display()}</small></p>
        <strong>Problem</strong>
        <p>{task.text}</p>
        {input_xhp}
        {output_xhp}
        <ul class="inline">
          <li>{submit_button}</li>
          <li id={"taskresponse"+str(task.id)}></li>
        </ul>
        {skip_button}
      </div>
      return page


class :cs:contest-problem-set(:x:element):
    attribute object contest @required,
              list ordered_tasks @required,
              dict task_by_id @required,
              dict score_by_task_id @required,
              int task_id
    children empty

    def render(self):
        # ordered_tasks is actually visible tasks!
        task_content = <div class="tab-content"></div>
        task_nav = <ul class="nav nav-tabs"></ul>
        display_task_id = int(self.getAttribute('task_id'))
        response = \
        <div class="tabbable tabs-left">
          {task_nav}
          {task_content}
        </div>

        ordered_tasks = self.getAttribute('ordered_tasks')
        task_by_id = self.getAttribute('task_by_id')
        score_by_task_id = self.getAttribute('score_by_task_id')
        if display_task_id == -1 and len(ordered_tasks) > 0:
              _, display_task_id = ordered_tasks[-1] # focus on the last one...
        for cnt, task_id in ordered_tasks:
            task = task_by_id[task_id]
            score = score_by_task_id.get(task_id)

            badge = <span class="label label-info">Untackled</span>
            score_str = '-'
            if score.solved:
                badge = <span class="label label-success">Solved</span>
            elif score.skipped:
                badge = <span class="label label-warning">Skipped</span>
            elif score.tries != 0:
                # Wrong answer on previous attempts
                badge = \
                <span class="label label-important">
                    Wrong answer
                </span>

            score_str = '{} ({})'.format(
                    score.score, score.format_tries())

            short_name = task.name
            if len(task.name) > 20:
              task.name=task.name[0:18] + '...'

            task_nav.appendChild(
                <li class={'active' if task_id==display_task_id else ''}>
                  <a data-toggle="tab" href={"#task_tab" + str(cnt+1)}>
                    {badge} {' '}
                    {task.name}
                  </a>
                </li>)
            task_content.appendChild(
                <div id={"task_tab" + str(cnt+1)}
                     class={"tab-pane active" if task_id==display_task_id else "tab-pane" }>
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
                    xhp = \
                    <x:frag>
                        <span class="badge badge-success">
                            {'{} ({})'.format(task_score.score,
                                task_score.format_tries())}
                        </span>
                    </x:frag>
                elif task_score.skipped:
                    xhp = \
                    <span class="badge badge-warning">
                        SK
                    </span>
                elif task_score.tries != 0:
                    xhp = \
                    <span class="badge badge-important">
                        WA ({task_score.format_tries()})
                    </span>
                else:
                    xhp = <span class="badge">-</span>
                task_scores.appendChild(<td class="task-score">{xhp}</td>)
            tbody.appendChild(
                <tr>
                    <td><cs:user user={user} /></td>
                    {task_scores}
                    <td>{score}</td>
                </tr>)

        return table


class :cs:contest-registration-list(:x:element):
    attribute object contest @required,
    children empty

    def render(self):
      contest = self.getAttribute('contest')

      tbody = <tbody />
      table = \
      <table class="table table-striped table-bordered">
          <thead>
              <tr>
                  <th>User</th>
              </tr>
          </thead>
          {tbody}
      </table>

      for user in contest.registered_users.all():
        tbody.appendChild(
          <tr>
            <td>
              <cs:user user={user} />
            </td>
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
          <div class="span3">{entry.time}</div>
          <div class="span2">{user_information}</div>
          <div class="span7">{log_information}</div>
        </div>


__all__ = ["xhpy_cs__header_contest", "xhpy_cs__header_home",
           "xhpy_cs__contest_list", "xhpy_cs__contest_problem_set",
           "xhpy_cs__contest_rankings", "xhpy_cs__task_show",
           "xhpy_cs__contest_registration_list",
           "xhpy_cs__log_entry"]
