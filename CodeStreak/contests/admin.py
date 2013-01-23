from django.contrib import admin
from CodeStreak.contests.models import Contest, Task, Score, Participation

admin.site.register(Contest)
admin.site.register(Task)
admin.site.register(Score)
admin.site.register(Participation)
