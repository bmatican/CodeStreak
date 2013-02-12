# Copyright 2012 Bogdan-Cristian Tataroiu

from django.core.context_processors import csrf
from django.conf import settings
from django.contrib import messages
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
            if 'request' in child._xhpyAttributeDeclaration():
                child.setAttribute('request', request)
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
            <div id="fb-root" />
            <script type="text/javascript">{ """
                var facebookAppId = '{}';
                var staticUrl = '{}';
            """.format(settings.FACEBOOK_APP_ID, settings.STATIC_URL)
            }</script>
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
    attribute float time_left,
              object request
    children :cs:header-link*, :cs:header-separator*

    def get_prepended_children(self):
        return <x:frag />

    def get_time_left(self):
        return self.getAttribute('time_left')

    def render(self):
        request = self.getAttribute('request')
        user = request.user
        time_left = self.get_time_left()
        if user.is_authenticated():
            user_info = \
            <li class="dropdown">
                <a class="dropdown-toggle" data-toggle="dropdown" href="#">
                    <cs:user user={user} />
                </a>
                <ul class="dropdown-menu" role="menu">
                    <li>
                        <a tabindex="-1" href="#">
                            View Profile (coming soon)
                        </a>
                    </li>
                    <li class="divider"></li>
                    <li>
                        <a tabindex="-1" href={settings.LOGOUT_URL}>
                            Log out
                        </a>
                    </li>
                </ul>
            </li>
        else:
            user_info = \
            <li>
                <form action="/facebook/connect/?facebook_login=1"
                    method="post">
                    <input type="hidden" value="/" name="next" />
                    <button id="facebook-button" type="button"
                        class="btn btn-primary pull-right"
                        data-loading-text="Loading..."
                        onclick="F.connect(this.parentNode); return false;">
                        Connect with Facebook
                    </button>
                </form>
            </li>

        return \
        <div class="navbar navbar-fixed-top">
            <div class="navbar-inner">
                <div class="container">
                    <a class="brand" href="/">
                        CodeStreak
                    </a>
                    <ul class="nav">
                        {self.get_prepended_children()}
                        {self.getChildren()}
                    </ul>
                    <ul class="nav pull-right">
                        {user_info}
                    </ul>
                    {<div class="navbar-text pull-right">
                        <span id="time-left" class={int(time_left)}></span>
                    </div>
                    if time_left else <x:frag />}
                </div>
            </div>
        </div>


class :cs:header-link(:x:element):
    attribute str link @required,
              bool active = False,
              bool post = False,
              object request
    children any

    def render(self):
        xhp = <li />
        if self.getAttribute('post'):
            if not self.getAttribute('request'):
                raise Exception('request attribute required for post links')
            xhp.appendChild(
                <form class="form-post-link" method="post"
                    action={self.getAttribute('link')}>
                    <cs:csrf request={self.getAttribute('request')} />
                    <button class="btn btn-link">
                        {self.getChildren()}
                    </button>
                </form>)
        else:
            xhp.appendChild(
                <a href={self.getAttribute('link')}>
                    {self.getChildren()}
                </a>)

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
        messages_xhp = <div id="alerts" class="alerts" />
        for message in messages:
            messages_xhp.appendChild(
                <div class={"alert alert-{}".format(message.tags)}>
                    <button type="button" class="close"
                        data-dismiss="alert">x</button>
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


class :cs:user(:x:element):
    attribute object user @required
    children empty

    def render(self):
        user = self.getAttribute('user')
        if user.first_name and user.last_name:
            user_displayname = user.first_name + ' ' + user.last_name
        else:
            user_displayname = user.username
        fb_user = FacebookProfile.objects.filter(user_id = user.id)
        if len(fb_user) > 0 and fb_user[0].image:
            fb_image = fb_user[0].image.url
        else:
            fb_image = None

        return \
        <span class="user">
            {<img class="user-img" src={fb_image} />
              if fb_image else <x:frag />}
            {user_displayname}
        </span>


class :cs:csrf(:x:element):
    attribute object request @required
    children empty

    def render(self):
        csrf_token = csrf(self.getAttribute('request'))['csrf_token']
        return \
        <input type="hidden" name="csrfmiddlewaretoken" value={csrf_token} />
