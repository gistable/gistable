import cgi

from google.appengine.api import mail
from google.appengine.ext import deferred

from ndb import model
from tipfy.routing import url_for
from tipfyext.ndb.mixins import DateMixin


class _FormattableContent(model.Model):
    raw = model.TextProperty(required=True)
    html = model.TextProperty(required=False)

class _DisplayState(model.Model):
    """Structured Property for listing User Keys and the
        state of the Message / Thread for that user
    """
    user_key = model.KeyProperty()
    # State assumes a certain flow, i.e. a message cannot be
    # archived until it has been read.
    # 0 - unread
    # 1 - read
    # 2 - archived
    # 3 - deleted
    # 4 - reported
    state = model.IntegerProperty(default=0)

    @staticmethod
    def label_to_integer(label):
        if label == 'unread':
            return 0
        if label == 'read':
            return 1
        if label == 'archived':
            return 2
        if label == 'deleted':
            return 3
        if label == 'reported':
            return 4

class Message(model.Model, DateMixin):
    sender_key = model.KeyProperty()
    subject = model.StringProperty()
    body = model.LocalStructuredProperty(_FormattableContent)
    recipients = model.StructuredProperty(_DisplayState, repeated=True)

    @property
    def sent_at(self):
        return self.created

    @property
    def sender(self):
        """
        :return:
            A User object from the stored sender_key
        """
        return self.sender_key.get()

    @classmethod
    def create(cls, sender_key, body, recipient_keys, **kwargs):
        """Creates a new message and returns it.

        :param sender_key:
            Key of the message sender.
        :param body:
            The raw message body, usually coming from a text field.
        :return:
            The newly created message.
        """
        kwargs['sender_key'] = sender_key
        if not kwargs['subject']:
            kwargs['subject'] = '%s...' % body[0:25]
        escaped_body = cgi.escape(body)
        html_body = escaped_body
        kwargs['body'] = _FormattableContent(raw=body, html=html_body)
        message = cls(**kwargs)
        message.recipients = [_DisplayState(user_key=r, state=0)
                              for r in recipient_keys]
        message.put()
        return message

class Thread(model.Model, DateMixin):
    message_keys = model.KeyProperty(repeated=True)
    private = model.BooleanProperty(default=False)
    participants = model.StructuredProperty(_DisplayState, repeated=True)

    @property
    def messages(self):
        return model.get_multi(self.message_keys)

    @property
    def latest_message(self):
        if self.messages:
            messages = self.messages
            msg_len = len(messages)
            return messages[msg_len - 1]
        else:
            return None

    @property
    def latest_subject(self):
        return self.latest_message.subject

    @property
    def senders(self):
        return [m.sender for m in self.messages]

    @property
    def latest_sender(self):
        return self.latest_message.sender

    def add_participant(self, new_user_key, state=0):
        """
        
        :param new_user_key:
        :param state:
        :return:
        """
        new_participant = _DisplayState(user_key=new_user_key, state=state)
        self.participants.append(new_participant)
        return self.participants

    def add_participants(self, user_keys):
        existing_user_keys = [p.user_key for p in self.participants]
        new_user_keys = set(user_keys) - set(existing_user_keys)
        for new_user_key in new_user_keys:
            self.add_participant(new_user_key)
        return self.participants

    @classmethod
    def get_active(cls, user_key):
        """Active threads are threads in the User's inbox
        """
        return cls.query(
            cls.participants.user_key == user_key,
            cls.participants.state <= 1,
        )

    @classmethod
    def get_archived(cls, user_key):
        """Archived threads are threads that have the state set to
        `archived` by the user
        """
        return cls.query(
            cls.participants.user_key == user_key,
            cls.participants.state == 2
        )

    @classmethod
    def get_reported(cls, user_key):
        """Reported threads are threads that have been marked as
        Spam by the user
        """
        return cls.query().filter(
            cls.participants.user_key == user_key,
            cls.participants.state == 4
        )

    @classmethod
    def get_private(cls, sender_key, recipient_key):
        """Get or create the private thread for two Users.

        Private threads are threads that only have 2 participants.

        :param sender_key:
            Key or the message sender
        :param recipient_key:
            Key or the message recipient
        :return:
            Query object.
        """
        return cls.query(cls.private == True,
                         cls.participants.user_key == sender_key,
                         cls.participants.user_key == recipient_key)

        
    @classmethod
    def create_message(cls, sender_id, body, recipient_ids=None,
                       subject=None, thread_id=None, thread=None, **kwargs):
        """Create a message from a user with recipient(s) and optional thread

        """
        # if we were pass a thread;
        if thread_id and not thread:
            thread = thread_id.get()
        if not recipient_ids:
            recipient_ids = [p.user_key for p in thread.participants]
        if not isinstance(recipient_ids, list):
            recipient_ids = [recipient_ids]
        if not thread:
            if len(recipient_ids) is 1:
                qry = cls.get_private(
                    sender_id,
                    recipient_ids[0]
                )
                thread = qry.get()
                if not thread:
                    thread = Thread(
                        private=True
                    )
            else:
                thread = Thread(
                    private=False
                )

        message = Message.create(
            sender_key=sender_id,
            recipient_keys=recipient_ids,
            subject=subject,
            body=body,
        )

        thread.message_keys.append(message.key)

        recipient_ids.append(sender_id)
        thread.add_participants(recipient_ids)
        thread.put()

        return thread

