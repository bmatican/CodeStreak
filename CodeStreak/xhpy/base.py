# Copyright 2012 Bogdan-Cristian Tataroiu

from django.conf import settings

from CodeStreak.xhpy.lib import *


class :cs:page(:x:element):
    attribute str title @required
    children :cs:header, :cs:content, :cs:footer

    def render(self):
        css_files = [
            settings.STATIC_URL + 'css/bootstrap.min.css',
            settings.STATIC_URL + 'css/bootstrap-responsive.min.css',
            settings.STATIC_URL + 'css/cs-base.css',
        ]
        js_files = [
            '://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js',
            settings.STATIC_URL + 'js/bootstrap.min.js',
        ]

        # Compose head of page
        head = \
        <head>
            <title>{self.getAttribute('title')}</title>
        </head>

        # Compose body of page
        body_container = \
        <div class="container">
            {self.getChildren('cs:content')}
            {self.getChildren('cs:footer')}
        </div>
        body = \
        <body>
            {self.getChildren('cs:header')}
            {body_container}
        </body>

        # Add CSS files to header
        for css_file in css_files:
            head.appendChild(
                <link href={css_file} rel="stylesheet" />)

        # Add JS files to end of body, so the pages load fast
        for js_file in js_files:
            body.appendChild(
                <script type="text/javascript" src={js_file} />)

        # Compose the page
        return \
        <x:doctype>
            <html>
                {head}
                {body}
            </html>
        </x:doctype>


class :cs:header(:x:element):
    attribute float end_timestamp

    def render(self):
        end_timestamp = self.getAttribute('end_timestamp')
        return \
        <div class="navbar navbar-fixed-top">
            <div class="navbar-inner">
                <div class="container">
                    <a class="brand" href="">
                        CodeStreak
                    </a>
                    <ul class="nav" id="navTabs">
                        <li class="active">
                            <a href="#contestlist">
                                Contest List
                            </a>
                        </li>
                        <li>
                            <a href="#problemset">
                                Problem Set
                            </a>
                        </li>
                        <li>
                            <a href="#rankings">
                                Rankings
                            </a>
                        </li>
                    </ul>
                    {<div class="navbar-text pull-right">Time left:{' '}
                        <span id="timeLeft" class={end_timestamp}>
                            00:00:00
                        </span>
                    </div>
                    if end_timestamp else <x:frag />}
                </div>
            </div>
        </div>


class :cs:content(:x:element):
    def render(self):
        return \
        <div class="main-content">
            {self.getChildren()}
        </div>


class :cs:footer(:x:element):
    def render(self):
        copyright_holders = \
        <x:frag>
        </x:frag>
        first = False
        for name, email in settings.ADMINS:
            if first:
                copyright_holders.appendChild(', ')
            else:
                first = True
            copyright_holders.appendChild(
                <a href={'mailto:' + email}>{name}</a>)

        return \
        <x:frag>
            <hr />
            <footer class="footer">
                <p class="pull-right">
                    <a href="#">Back to top</a>
                </p>
                <p>
                    Copyright 2012{' '}{copyright_holders}
                </p>
            </footer>
        </x:frag>
