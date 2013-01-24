from django.conf import settings
from django.core.urlresolvers import reverse as url_reverse

from CodeStreak.xhpy.base import *


class :cs:header-home(:cs:header):
    def render(self):
        self.prepended_children = \
        <cs:header-link link={url_reverse('contest-list')} active={True}>
            Contest List
        </cs:header-link>

        return super(:cs:header-home, self).render()


class :cs:header-contest(:cs:header):
    attribute float end_timestamp,
              object contest @required,
              bool active_home = True

    def render(self):
        contest = self.getAttribute('contest')
        active_home = self.getAttribute('active_home')

        self.prepended_children = \
        <x:frag>
            <cs:header-link
                link={url_reverse('contest-list')}>
                Contest List
            </cs:header-link>
            <cs:header-separator />
            <li class="navbar-contest-name">{contest.name}</li>
            <cs:header-link
                link={url_reverse('contest-home', args=(contest.id,))}
                active={active_home}>
                Problems
            </cs:header-link>
            <cs:header-link
                link={url_reverse('contest-ranking', args=(contest.id,))}
                active={not active_home}>
                Rankings
            </cs:header-link>
        </x:frag>

        return super(:cs:header-contest, self).render()


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

__all__ = ["xhpy_cs__header_contest", "xhpy_cs__header_home", "xhpy_cs__contest_list"]
