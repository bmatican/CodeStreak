from django.conf import settings
from django.core.urlresolvers import reverse as url_reverse
from django.utils.timezone import now

from CodeStreak.xhpy.base import *
from CodeStreak.contests.models import Participation


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


class :cs:contest-problem-set(:x:element):
    attribute object contest @required,
              list ordered_tasks @required,
              dict task_by_id @required,
              dict score_by_task_id @required
    children empty

    def render(self):
        tbody = <tbody />
        table = \
        <table class="table table-striped table-bordered">
            <thead>
                <tr>
                    <th></th>
                    <th>Problem name</th>
                    <th>Score</th>
                </tr>
            </thead>
            {tbody}
        </table>

        ordered_tasks = self.getAttribute('ordered_tasks')
        task_by_id = self.getAttribute('task_by_id')
        score_by_task_id = self.getAttribute('score_by_task_id')
        for cnt, task_id in ordered_tasks:
            task = task_by_id[task_id]
            score = score_by_task_id.get(task_id)

            row_class = 'info'
            score_str = '-'
            if score:
                if score.solved:
                    row_class = 'success'
                elif score.skipped:
                    row_class = 'warning'
                else:
                    row_class = 'error'

                score_str = '{} ({} {})'.format(score.score,
                        score.tries + 1,
                        'try' if score.tries + 1 == 1 else 'tries')
            task_url = url_reverse('task-view', args=(task.id,))

            tbody.appendChild(
                <tr class={row_class}>
                    <td><a href={task_url}>{cnt + 1}</a></td>
                    <td><a href={task_url}>{task.name}</a></td>
                    <td>{score_str}</td>
                </tr>)

        return table


__all__ = ["xhpy_cs__header_contest", "xhpy_cs__header_home",
           "xhpy_cs__contest_list", "xhpy_cs__contest_problem_set"]
