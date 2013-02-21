from django.contrib import admin
from django.contrib.sites.models import Site

from CodeStreak.contests.models import Contest, Task, Score, Participation, \
    LogEntry

admin.site.register(Contest)
admin.site.register(Task)
admin.site.register(Score)
admin.site.register(Participation)
admin.site.register(LogEntry)
