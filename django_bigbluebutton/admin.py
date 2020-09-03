from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, re_path, path

from django.utils.html import format_html

from .bbb import BigBlueButton
from .models import Meeting
from .forms import MeetingCreateLinkForm


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    search_fields = ['name', 'meeting_id']
    list_display = (
        'id', 'name', 'meeting_id', 'created_at',
        'is_running', 'meeting_actions'
    )
    actions = ["refresh_meetings_running_status"]
    list_per_page = 30

    def meeting_join(self, request, meeting_id, *args, **kwargs):
        """ Will try to call join API of bigbluebutton and
        get a join link to meeting with provided meeting_id.
        And will redirect to join link. """
        meeting = self.get_object(request, meeting_id)
        link = meeting.create_join_link('Administrator', 'moderator')
        return HttpResponseRedirect(link)

    def create_meeting_link(self, request, meeting_id, *args, **kwargs):
        """ Will create meeting with meeting_id if not exist,
        Will join as moderator access. This method is for fast
        join to a meeting as admin.
        You can get same functionality with join meeting too,
        But should change user_type to 'moderator' for that. """
        meeting = self.get_object(request, meeting_id)
        context = self.admin_site.each_context(request)

        if request.method != 'POST':
            # If method is not post, then just render the form
            form = MeetingCreateLinkForm()
        else:
            form = MeetingCreateLinkForm(request.POST)
            if form.is_valid():
                # Now call create_link method and pass meeting
                # Object to it. create_link is located in
                # MeetingCreateLinkForm class in forms.py
                context['link'] = form.create_link(meeting)
            else:
                print('error not is_valid()')
                self.message_user(request, 'Success')
                url = reverse(
                    'admin:meeting-create-link',
                    args=[meeting.pk],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context['opts'] = self.model._meta
        context['form'] = form
        context['meeting'] = meeting
        context['title'] = meeting.name
        return TemplateResponse(
            request,
            'admin/meeting_create_link.html',
            context,
        )

    def get_urls(self):
        """ All extra URLs are defined here."""
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<meeting_id>.+)/join/$',
                self.admin_site.admin_view(self.meeting_join),
                name='meeting-join',
            ),
            re_path(
                r'^(?P<meeting_id>.+)/create-link/$',
                self.admin_site.admin_view(self.create_meeting_link),
                name='meeting-create-link',
            ),
            path('refresh-meetings/', self.refresh_meetings_running_status),
        ]
        return custom_urls + urls

    def meeting_actions(self, obj):
        """ This actions will be placed in front of each row of table list.
        For example here we registered two buttons:
        - Join Now: Which will call url 'admin:meeting-join'
        - Create Join Link: Which will cal url 'admin:meeting-create-link'
        """
        return format_html(
            '<a class="button" href="{}">Join Now</a>&nbsp;'
            '<a class="button" href="{}">Create Join link</a>&nbsp;',
            reverse('admin:meeting-join', args=[obj.pk]),
            reverse('admin:meeting-create-link', args=[obj.pk]),
        )

    meeting_actions.short_description = 'Actions'
    meeting_actions.allow_tags = True

    def refresh_meetings_running_status(self, request):
        running_meetings = BigBlueButton().get_meetings()
        print(running_meetings)
        return HttpResponseRedirect("../")

    refresh_meetings_running_status.short_description = "Refresh Meetings"
