"""
Interface for messages.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import abc as _abc
import typing as _t

from _sassy.d_sassy import Message


class MessagesInterfaces(_abc.ABC):
    """Message abstract class (Interface)."""

    @_abc.abstractmethod
    def msg(self, name: str, extra: _t.Optional[str] = None) -> Message:
        """
        Read a message.

        Args:
            name (str): The message name.
            extra (Optional[str]): Extra information.

        Returns (Message):
            A ``Message`` :abbr:`DTO (Data Transfer Object)`.
        """
        raise NotImplementedError
