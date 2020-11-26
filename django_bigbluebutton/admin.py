from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, re_path, path

from django.utils.html import format_html

from .models import Meeting
from .forms import MeetingCreateLinkForm
from .settings import UPDATE_RUNNING_ON_EACH_CALL


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    search_fields = ['name', 'meeting_id']
    list_display = (
        'id', 'name', 'meeting_id', 'created_at',
        'is_running', 'meeting_actions'
    )
    actions = ["update_running_meetings"] if not UPDATE_RUNNING_ON_EACH_CALL else []
    list_per_page = 30

    def get_queryset(self, request):
        qs = super(MeetingAdmin, self).get_queryset(request)

        # If settings.UPDATE_RUNNING_ON_EACH_CALL, then on each call
        # For queryset, call getMeetings and update status of meetings
        if UPDATE_RUNNING_ON_EACH_CALL:
            Meeting.update_running_meetings()

        return qs

    def join_meeting_action(self, request, meeting_id, *args, **kwargs):
        """ Will try to call join API of bigbluebutton and
        get a join link to meeting with provided meeting_id.
        And will redirect to join link. """
        meeting = self.get_object(request, meeting_id)
        meeting.start()
        if not meeting.is_running:
            meeting.is_running = True
            meeting.save()
        return HttpResponseRedirect(reverse('admin:django_bigbluebutton_meeting_changelist'))

    def end_meeting_action(self, request, meeting_id, *args, **kwargs):
        """ Will call end() method from bigbluebutton,
        and then will update Meeting obj is_running status from local database"""
        meeting = self.get_object(request, meeting_id)
        ended = meeting.end()
        if ended:
            self.message_user(request, 'Success')
        else:
            self.message_user(request, 'Unable to close meeting', level=40)
        return HttpResponseRedirect(reverse('admin:django_bigbluebutton_meeting_changelist'))

    def create_meeting_link_action(self, request, meeting_id, *args, **kwargs):
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
                self.message_user(request, 'Error')
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
                self.admin_site.admin_view(self.join_meeting_action),
                name='meeting-join',
            ),
            re_path(
                r'^(?P<meeting_id>.+)/end/$',
                self.admin_site.admin_view(self.end_meeting_action),
                name='meeting-end',
            ),
            re_path(
                r'^(?P<meeting_id>.+)/create-link/$',
                self.admin_site.admin_view(self.create_meeting_link_action),
                name='meeting-create-link',
            ),
            path('refresh-meetings/', self.update_running_meetings),
        ]
        return custom_urls + urls

    def meeting_actions(self, obj):
        """ This actions will be placed in front of each row of table list.
        For example here we registered two buttons:
        - Join Now: Which will call url 'admin:meeting-join'
        - Create Join Link: Which will cal url 'admin:meeting-create-link'
        """

        create_join_link_href = '<a class="button"' \
                                'title="Will create meeting if not started yet, ' \
                                'and join to it as Administrator" href="{}">Create join link</a>'.format(
                                    reverse('admin:meeting-create-link', args=[obj.pk])
                                )
        start_meeting_href = '<a class="button" href="{}" style="background: green" ' \
                             'target="_blank">Start Now</a>&nbsp;'.format(
                                 reverse('admin:meeting-join', args=[obj.pk])
                             )
        end_meeting_href = '<a class="button" style="background: red" href="{}">End meeting</a>'.format(
                               reverse('admin:meeting-end', args=[obj.pk])
                           )
        return format_html(
            '{}&nbsp;{}'.format(
                create_join_link_href,
                start_meeting_href if not obj.is_running else end_meeting_href
            )
        )

    meeting_actions.short_description = 'Actions'
    meeting_actions.allow_tags = True

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'update_running_meetings':
            if not request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in self.model.objects.all():
                    post.update({admin.ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super(MeetingAdmin, self).changelist_view(request, extra_context)

    def update_running_meetings(self, request, *args, **kwargs):
        """ Will get list of running meetings from bigbluebutton,
        And update states of Meetings objects in database. """
        Meeting.update_running_meetings()
        return HttpResponseRedirect(".")

    update_running_meetings.short_description = "Refresh Meetings"
