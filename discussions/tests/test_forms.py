from django.test import TestCase
from django.contrib.auth.models import User

from discussions.forms import ComposeForm


class ComposeFormTests(TestCase):
    """ Test the compose form. """
    fixtures = ['users']

    def test_invalid_data(self):
        """
        Test the save method of :class:`ComposeForm`

        We don't need to make the ``to`` field sweat because we have done that
        in the ``fields`` test.

        """
        invalid_data_dicts = [
            # No body
            {'data': {'to': 'john',
                      'body': '',
                      'subject': ''},
             'error': ('body', [u'This field is required.'])},
        ]

        for invalid_dict in invalid_data_dicts:
            form = ComposeForm(data=invalid_dict['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]],
                             invalid_dict['error'][1])

    def test_save_msg(self):
        """ Test valid data """
        valid_data = {'to': 'thoas,ampelmann',
                      'body': 'Body',
                      'subject': 'subject'}

        form = ComposeForm(data=valid_data)

        self.failUnless(form.is_valid())

        # Save the form.
        sender = User.objects.get(username='oleiade')
        discussion = form.save(sender)

        # Check if the values are set correctly
        self.failUnlessEqual(discussion.subject, valid_data['subject'])

        self.assertEqual(discussion.messages.count(), 1)

        self.failUnlessEqual(discussion.sender, sender)
        self.failUnless(discussion.created_at)

        message = discussion.messages.all()[0]

        self.assertEqual(message.body, valid_data['body'])

        # Check recipients
        self.failUnlessEqual(discussion.recipients.all()[0].username, 'ampelmann')
        self.failUnlessEqual(discussion.recipients.all()[1].username, 'thoas')
