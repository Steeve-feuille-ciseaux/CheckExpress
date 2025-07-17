from django.contrib import admin
from .models import Licence, Presence, Session

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('licence', 'date', 'present')
    list_filter = ('date', 'present')

admin.site.register(Licence)
admin.site.register(Session)
