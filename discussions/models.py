from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import truncate_words

from discussions.managers import (DiscussionManager, DiscussionContactManager,
                                  DiscussionRecipientManager)

from model_utils import Choices


class DiscussionContact(models.Model):
    """
    Contact model.

    A contact is a user to whom a user has send a message to or
    received a message from.

    """
    from_user = models.ForeignKey(User, verbose_name=_('from user'),
                                  related_name=('from_users'))

    to_user = models.ForeignKey(User, verbose_name=_('to user'),
                                related_name=('to_users'))

    latest_discussion = models.ForeignKey('Discussion',
                                          verbose_name=_("latest discussion"))

    objects = DiscussionContactManager()

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['latest_discussion']
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    def __unicode__(self):
        return (_('%(from_user)s and %(to_user)s')
                % {'from_user': self.from_user.username,
                   'to_user': self.to_user.username})

    def opposite_user(self, user):
        """
        Returns the user opposite of the user that is given

        :param user:
            A Django :class:`User`.

        :return:
            A Django :class:`User`.

        """
        if self.from_user == user:
            return self.to_user

        return self.from_user


class DiscussionRecipient(models.Model):
    """
    Intermediate model to allow per recipient marking as
    deleted, read etc. of a message.

    """
    STATUS = Choices((0, 'read', _('read')),
                     (1, 'unread', _('unread')),
                     (2, 'deleted', _('deleted')))

    user = models.ForeignKey(User,
                             verbose_name=_('recipient'))

    discussion = models.ForeignKey('Discussion',
                                   verbose_name=_('message'))

    read_at = models.DateTimeField(_('read at'),
                                   null=True,
                                   blank=True)

    deleted_at = models.DateTimeField(_('recipient deleted at'),
                                      null=True,
                                      blank=True)

    status = models.PositiveSmallIntegerField(choices=STATUS,
                                              default=STATUS.unread,
                                              verbose_name=_('Status'),
                                              db_index=True)

    objects = DiscussionRecipientManager()

    class Meta:
        verbose_name = _('recipient')
        verbose_name_plural = _('recipients')

    def __unicode__(self):
        return (_('%(discussion)s')
                % {'discussion': self.discussion})

    def is_read(self):
        """ Returns a boolean whether the recipient has read the message """
        return self.read_at is None

    def mark_as_deleted(self, commit=True):
        self.deleted_at = datetime.now()
        self.status = self.STATUS.deleted

        if commit:
            self.save()


class Discussion(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(User,
                               related_name='sent_discussions',
                               verbose_name=_('sender'))

    recipients = models.ManyToManyField(User,
                                        through='DiscussionRecipient',
                                        related_name='received_discussions',
                                        verbose_name=_('recipients'))

    objects = DiscussionManager()

    created_at = models.DateTimeField(_('created at'),
                                      auto_now_add=True)

    sender_deleted_at = models.DateTimeField(_("sender deleted at"),
                                             null=True,
                                             blank=True)

    subject = models.CharField(max_length=255)

    objects = DiscussionManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('discussion')
        verbose_name_plural = _('discussions')

    def __unicode__(self):
        return 'Discussion opened by %s' % self.sender

    def save_recipients(self, to_user_list):
        """
        Save the recipients for this message

        :param to_user_list:
            A list which elements are :class:`User` to whom the message is for.

        :return:
            Boolean indicating if any users are saved.

        """
        created = False
        for user in to_user_list:
            DiscussionRecipient.objects.create(user=user,
                                               discussion=self)
            created = True
        return created

    def update_contacts(self, to_user_list):
        """
        Updates the contacts that are used for this message.

        :param to_user_list:
            List of Django :class:`User`.

        :return:
            A boolean if a user is contact is updated.

        """
        updated = False
        for user in to_user_list:
            DiscussionContact.objects.update_contact(self.sender,
                                                     user,
                                                     self)
            updated = True
        return updated

    def add_message(self, body, sender=None):
        if not sender:
            sender = self.sender

        m = Message(sender=sender,
                    body=body,
                    discussion=self)
        m.save()

        return m


class Message(models.Model):
    """ Private message model, from user to user(s) """
    sender = models.ForeignKey(User,
                               related_name='sent_messages',
                               verbose_name=_('sender'))

    discussion = models.ForeignKey('Discussion',
                                   related_name='messages',
                                   verbose_name=_('discussion'))

    body = models.TextField(_('body'))

    sent_at = models.DateTimeField(_('sent at'),
                                   auto_now_add=True)

    sender_deleted_at = models.DateTimeField(_('sender deleted at'),
                                             null=True,
                                             blank=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __unicode__(self):
        """ Human representation, displaying first ten words of the body. """
        truncated_body = truncate_words(self.body, 10)
        return "%(truncated_body)s" % {'truncated_body': truncated_body}
