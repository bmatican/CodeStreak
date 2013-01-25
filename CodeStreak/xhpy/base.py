# Copyright 2012 Bogdan-Cristian Tataroiu

from django.conf import settings
from django.contrib import messages
from django.template import Context, loader
from django.template.context import RequestContext
from django_facebook.models import FacebookProfile

from CodeStreak.xhpy.lib import *


class :cs:page(:x:element):
    attribute str title @required,
              object request @required
    children :cs:header, :cs:content, :cs:footer

    def render(self):
        css_files = [
            settings.STATIC_URL + 'css/bootstrap.min.css',
            settings.STATIC_URL + 'css/bootstrap-responsive.min.css',
            settings.STATIC_URL + 'css/cs-base.css',
            settings.STATIC_URL + 'css/facebook.css',
        ]
        js_files = [
            settings.STATIC_URL + 'js/jquery-1.9.0.min.js',
            settings.STATIC_URL + 'js/bootstrap.min.js',
            settings.STATIC_URL + 'js/facebook.js',
            settings.STATIC_URL + 'js/base.js',
        ] 
        # Compose head of page
        head = \
        <head>
            <title>{self.getAttribute('title')}</title>
        </head>

        request = self.getAttribute('request')
        # Compose body of page
        for child in self.getChildren():
            if 'user' in child._xhpyAttributeDeclaration():
                child.setAttribute('user', request.user)
            if 'messages' in child._xhpyAttributeDeclaration():
                child.setAttribute('messages',
                                   messages.get_messages(request))
            if isinstance(child, :cs:header):
                header = child
            elif isinstance(child, :cs:content):
                content = child
            elif isinstance(child, :cs:footer):
                footer = child
        body = \
        <body>
            {header}
            <div class="container">
                {content}
                {footer}
            </div>
            <div id="fb-root">
            </div>
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
    attribute float end_timestamp,
              object user
    children :cs:header-link*, :cs:header-separator*

    def __init__(self, *args, **kwargs):
        super(:cs:header, self).__init__(*args, **kwargs)
        self.prepended_children = <x:frag />

    def render(self):
        user = self.getAttribute('user')
        end_timestamp = self.getAttribute('end_timestamp')
        fb_image = None
        user_displayname = None
        if user.is_authenticated():
          if user.first_name and user.last_name:
            user_displayname = user.first_name + ' ' + user.last_name
          else:
            user_displayname = user.username
          fb_user = FacebookProfile.objects.filter(user_id = user.id)
          if len(fb_user) > 0 and fb_user[0].image:
            fb_image = fb_user[0].image.url
            
        return \
        <div class="navbar navbar-fixed-top">
            <div class="navbar-inner">
                <div class="container">
                    <a class="brand" href="/">
                        CodeStreak
                    </a>
                    <ul class="nav">
                        {self.prepended_children}
                        {self.getChildren()}
                    </ul>
                    { <div class="navbar-text pull-right">
                        {user_displayname}
                        {<img src={fb_image} />
                         if fb_image else <x:frag />}
                      </div>
                      if user.is_authenticated() else
                      <form action="/facebook/connect/?facebook_login=1" method="post">
                        <input type="hidden" value="" name="next" />
                        <button id="facebook-button" type="button" class="btn \
                            btn-primary pull-right" data-loading-text="Loading..." \
                            onclick="F.connect(this.parentNode); return false;">
                          Connect with Facebook
                        </button>
                      </form>}
                    {<div class="navbar-text pull-right">Time left:{' '}
                        <span id="timeLeft" class={end_timestamp}>
                            00:00:00
                        </span>
                    </div>
                    if end_timestamp else <x:frag />}
                </div>
            </div>
        </div>


class :cs:header-link(:x:element):
    attribute str link @required,
              bool active = False
    children any

    def render(self):
        xhp = \
        <li>
            <a href={self.getAttribute('link')}>
                {self.getChildren()}
            </a>
        </li>

        if self.getAttribute('active'):
            xhp.setAttribute('class', 'active')

        return xhp


class :cs:header-separator(:x:element):
    children empty

    def render(self):
        return <li class="divider-vertical" />


class :cs:content(:x:element):
    attribute list messages @required
    children any

    def render(self):
        messages = self.getAttribute('messages')
        messages_xhp = <div class="alerts" />
        for message in messages:
            messages_xhp.appendChild(
                <div class={"alert alert-{}".format(message.tags)}>
                    {message.message}
                </div>)

        return \
        <div class="main-content">
            {messages_xhp}
            {self.getChildren()}
        </div>


class :cs:footer(:x:element):
    children empty

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
