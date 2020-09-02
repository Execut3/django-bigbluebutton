from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse, re_path

from django.utils.html import format_html

from .models import Meeting
from .forms import MeetingCreateLinkForm


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    search_fields = ['name', 'meeting_id']
    list_display = ('id', 'name', 'meeting_id', 'created_at', 'account_actions')
    list_per_page = 30

    def meeting_join(self, request, meeting_id, *args, **kwargs):
        print(meeting_id)
        meeting = self.get_object(request, meeting_id)
        link = meeting.create_join_link('Administrator', 'moderator')
        return HttpResponseRedirect(link)

    def create_meeting_link(self, request, meeting_id, *args, **kwargs):
        print(meeting_id)
        meeting = self.get_object(request, meeting_id)
        context = self.admin_site.each_context(request)

        if request.method != 'POST':
            form = MeetingCreateLinkForm()
        else:
            form = MeetingCreateLinkForm(request.POST)
            if form.is_valid():
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
        ]
        return custom_urls + urls

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Join Now</a>&nbsp;'
            '<a class="button" href="{}">Create Join link</a>&nbsp;',
            reverse('admin:meeting-join', args=[obj.pk]),
            reverse('admin:meeting-create-link', args=[obj.pk]),
        )

    account_actions.short_description = 'Actions'
    account_actions.allow_tags = True
