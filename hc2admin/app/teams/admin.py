
from django.contrib import admin

from hc2admin.admin import ReadOnlyAdmin
from teams.models   import Team

admin.site.register( Team, ReadOnlyAdmin )
