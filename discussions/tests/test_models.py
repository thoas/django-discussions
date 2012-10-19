from django.test import TestCase
from django.utils.text import truncate_words
from django.contrib.auth.models import User

from discussions.models import Message, DiscussionRecipient, DiscussionContact


class MessageContactTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        contact = DiscussionContact.objects.get(pk=1)
        correct_format = "thoas and ampelmann"
        self.failUnlessEqual(contact.__unicode__(),
                             correct_format)

    def test_opposite_user(self):
        """ Test if the opposite user is returned """
        contact = DiscussionContact.objects.get(pk=1)
        thoas = User.objects.get(pk=1)
        ampelmann = User.objects.get(pk=2)

        # Test the opposites
        self.failUnlessEqual(contact.opposite_user(thoas),
                             ampelmann)

        self.failUnlessEqual(contact.opposite_user(ampelmann),
                             thoas)


class MessageModelTests(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a message """
        message = Message.objects.get(pk=1)
        truncated_body = truncate_words(message.body, 10)
        self.failUnlessEqual(message.__unicode__(),
                             truncated_body)


class MessageRecipientModelTest(TestCase):
    fixtures = ['users', 'messages']

    def test_string_formatting(self):
        """ Test the human representation of a recipient """
        recipient = DiscussionRecipient.objects.get(pk=1)

        valid_unicode = '%s' % (recipient.discussion)

        self.failUnlessEqual(recipient.__unicode__(),
                             valid_unicode)

    def test_new(self):
        """ Test if the message that is new is correct """
        new_message = DiscussionRecipient.objects.get(pk=1)
        read_message = DiscussionRecipient.objects.get(pk=2)

        self.failUnless(new_message.is_read())
        self.failIf(read_message.is_read())
