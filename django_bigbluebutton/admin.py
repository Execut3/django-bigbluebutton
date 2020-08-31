from django.contrib import admin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    search_fields = ['name', 'meeting_id']
    list_display = ('id', 'name', 'meeting_id', 'created_at')
    list_per_page = 30
