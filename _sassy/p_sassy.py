"""
Service for Sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import os
import typing as _t

import yaml

from _sassy.d_sassy import Message
from _sassy.i_sassy import MessagesInterfaces

_MESSAGES_FILE = 'messages.yml'
_PATH = os.path.dirname(os.path.abspath(__file__))


class MessageService(MessagesInterfaces):
    """Message Service class."""

    def __init__(self):
        """Init instance."""
        self.messages: _t.Optional[_t.Dict[str, _t.Any]] = None
        self.message_file = "/".join([_PATH, _MESSAGES_FILE])
        self.load_messages()

    def load_messages(self):
        """Set messages."""
        if not self.messages:
            with open(self.message_file) as file:
                self.messages = yaml.load(file, Loader=yaml.Loader)

    def msg(
            self,
            name: str,
            extra: _t.Optional[str] = None
    ) -> Message:
        """
        Read a message.

        Args:
            name (str): The message name.
            extra (Optional[str]): Extra information.

        Returns (Message):
            A ``Message`` :abbr:`DTO (Data Transfer Object)`.
        """
        if name not in self.messages:
            msg = self.messages['error_msg']
            extra = name
        else:
            msg = self.messages[name]

        code = msg['code']
        severity = self.messages['severity'][int(str(msg['code'])[0])]
        text = msg['text']

        message = Message(
            code=code,
            severity=severity
        )
        message.extra = extra
        message.text = text

        return message
