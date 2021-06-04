from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import Group

from django_messages.utils import get_user_model

User = get_user_model()

from django_messages.models import Message


class MessageAdminForm(forms.ModelForm):
    group = forms.ChoiceField(label=_('group'), required=False,
                              help_text=_('Creates the message optionally for all users or a group of users.'))

    def __init__(self, *args, **kwargs):
        super(MessageAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].choices = self._get_group_choices()
        self.fields['recipient'].required = True

    def _get_group_choices(self):
        return [('', u'---------'), ('all', _('All users'))] + \
               [(group.pk, group.name) for group in Group.objects.all()]

    class Meta:
        model = Message
        fields = ('sender', 'recipient', 'group', 'parent_msg', 'subject',
                  'body', 'sent_at', 'read_at', 'replied_at', 'sender_deleted_at',
                  'recipient_deleted_at')


class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    fieldsets = (
        (None, {
            'fields': (
                'sender',
                ('recipient', 'group'),
            ),
        }),
        (_('Message'), {
            'fields': (
                'parent_msg',
                'subject', 'body',
            ),
            'classes': ('monospace'),
        }),
        (_('Date/time'), {
            'fields': (
                'sent_at', 'read_at', 'replied_at',
                'sender_deleted_at', 'recipient_deleted_at',
            ),
            'classes': ('collapse', 'wide'),
        }),
    )
    list_display = ('subject', 'sender', 'recipient', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'sender', 'recipient')
    search_fields = ('subject', 'body')
    raw_id_fields = ('sender', 'recipient', 'parent_msg')

    def save_model(self, request, obj, form, change):

        obj.save()

        if form.cleaned_data['group'] == 'all':
            recipients = User.objects.exclude(pk=obj.recipient.pk)
        else:
            recipients = []
            group = form.cleaned_data['group']
            if group:
                group = Group.objects.get(pk=group)
                recipients.extend(
                    list(group.user_set.exclude(pk=obj.recipient.pk)))
        for user in recipients:
            obj.pk = None
            obj.recipient = user
            obj.save()


admin.site.register(Message, MessageAdmin)
