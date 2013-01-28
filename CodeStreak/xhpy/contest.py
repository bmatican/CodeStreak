from django.conf import settings
from django.core.urlresolvers import reverse as url_reverse
from django.utils.timezone import now

from CodeStreak.xhpy.base import *
from CodeStreak.contests.models import Score, Participation
from CodeStreak.contests.utils.tasks import InvalidProblemOrderingException


class :cs:header-home(:cs:header):
    def get_prepended_children(self):
        return \
        <cs:header-link link={url_reverse('contest-list')} active={True}>
            Contest List
        </cs:header-link>


class :cs:header-contest(:cs:header):
    attribute float end_timestamp,
              object contest @required,
              object user,
              str active_tab = 'content-home'

    def get_prepended_children(self):
        contest = self.getAttribute('contest')
        user = self.getAttribute('user')
        active_tab = self.getAttribute('active_tab')

        prepended_children = \
        <x:frag>
            <cs:header-link
                link={url_reverse('contest-list')}>
                Contest List
            </cs:header-link>
            <cs:header-separator />
            <li class="navbar-contest-name">{contest.name}</li>
            <cs:header-link
                link={url_reverse('contest-home', args=(contest.id,))}
                active={active_tab == 'contest-home'}>
                Problems
            </cs:header-link>
            <cs:header-link
                link={url_reverse('contest-ranking', args=(contest.id,))}
                active={active_tab == 'contest-ranking'}>
                Rankings
            </cs:header-link>
        </x:frag>
        if user.is_authenticated() and contest.start_date > now():
            try:
                Participation.get_entry(contest.id, user.id)
                content = 'Unregister'
                link = url_reverse('contest-unregister', args=(contest.id,))
            except Participation.DoesNotExist:
                content = 'Register'
                link = url_reverse('contest-register', args=(contest.id,))
            prepended_children.appendChild(
                <cs:header-link
                    link={link}
                    active={active_tab == 'contest-register'}>
                    {content}
                </cs:header-link>)
        if user.is_staff:
          content = 'Logs'
          link = url_reverse('contest-logs', args=(contest.id,))
          prepended_children.appendChild(
              <cs:header-link
                  link={link}
                  active={active_tab == 'contest-logs'}>
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
                    <td><a href={contest_url}>{contest.start_date}</a></td>
                    <td>{contest.get_registered_user_count()}</td>
                    <td>{contest.get_assigned_task_count()}</td>
                </tr>)

        return table

class :cs:task-show(:x:element):
    attribute object task @required
    children empty

    def render(self):
      task = self.getAttribute('task')
      page = \
      <div>
        <blockquote>
          <p> <small> { "Difficulty: " + task.get_difficulty_display() } </small> </p>
          <strong>Problem</strong>
          <p>{ task.text } </p><br />
          { <div>
              <strong>Input</strong> <br />
              <code>{task.input}</code>
            </div>
            if task.input else <x:frag />}
        </blockquote>
        <table><tr><td>
          <div class="input-append">
            <input class="span2" id={"taskanswer"+str(task.id)} type="text"
                placeholder="Type answer..." />
            <button class="btn" type="button" id={"answerbutton" + str(task.id)} onClick={"submitTask(" +str(task.id) + ")"} data-loading-text="Loading...">
              Submit!
            </button>
          </div>
        </td><td>
          {' '}<div id={"taskresponse"+str(task.id)}></div>
        </td></tr></table>
      </div>
      return page

class :cs:contest-problem-set(:x:element):
    attribute object contest @required,
              list ordered_tasks @required,
              dict task_by_id @required,
              dict score_by_task_id @required
    children empty

    def render(self):
        response = <div class="accordion" id="accordion2"></div>

        ordered_tasks = self.getAttribute('ordered_tasks')
        task_by_id = self.getAttribute('task_by_id')
        score_by_task_id = self.getAttribute('score_by_task_id')
        for cnt, task_id in ordered_tasks:
            task = task_by_id[task_id]
            score = score_by_task_id.get(task_id)

            badge = <span class="label label-info">Untackled</span>
            score_str = '-'
            if score:
                if score.solved:
                    badge = <span class="label label-success">Solved</span>
                elif score.skipped:
                    badge = <span class="label label-warning">Skipped</span>
                else:
                    # Wrong answer on previous attempts
                    badge = \
                    <span class="label label-important">
                        Wrong answer
                    </span>

                score_str = '{} ({})'.format(
                        score.score, score.format_tries())
            task_url = url_reverse('task-view', args=(task.id,))

            response.appendChild(
              <div class="accordion-group">
                <div class="accordion-heading">
                   { ' ' }{badge} { ' ' }
                  <a data-toggle="collapse"
                      data-parent="#accordion2" href={"#collapse" + str(cnt+1)}>
                    {task.name }
                  </a>
                </div>
                <div id={"collapse" + str(cnt+1)} class="accordion-body collapse in">
                  <div class="accordion-inner">
                    <cs:task-show task={task} />
                  </div>
                </div>
              </div>

            )

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
                url_reverse('contest-home', args=(contest.id,)), task.id)
            header_tasks.appendChild(
                <th class="task-score">
                    <a href={task_url} rel="tooltip" title={task.name}>
                        {task.id}
                    </a>
                </th>)

        tbody = <tbody />
        table = \
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th>Team</th>
                    {header_tasks}
                    <th>Score</th>
                </tr>
            </thead>
            {tbody}
        </table>

        for participation in rankings:
            user = participation.user
            if user.first_name and user.last_name:
                user_displayname = user.first_name + ' ' + user.last_name
            else:
                user_displayname = user.username
            score = participation.score

            task_scores = <x:frag />
            scores_per_task = Score.get_scores(contest.id, user.id)
            for task in tasks:
                if len(scores_per_task):
                    if scores_per_task[0].task_id != task.id:
                        raise InvalidProblemOrderingException
                    task_score = scores_per_task[0]
                    scores_per_task = scores_per_task[1:]
                else:
                    task_score = None

                if task_score == None:
                    xhp = <span class="badge">-</span>
                elif task_score.solved:
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
                else:
                    xhp = \
                    <span class="badge badge-important">
                        WA ({task_score.format_tries()})
                    </span>
                task_scores.appendChild(<td class="task-score">{xhp}</td>)
            tbody.appendChild(
                <tr>
                    <td>{user_displayname}</td>
                    {task_scores}
                    <td>{score}</td>
                </tr>)

        return table


__all__ = ["xhpy_cs__header_contest", "xhpy_cs__header_home",
           "xhpy_cs__contest_list", "xhpy_cs__contest_problem_set",
           "xhpy_cs__contest_rankings", "xhpy_cs__task_show"]
