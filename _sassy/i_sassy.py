"""
Interface for messages.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import abc as _abc

from _sassy.d_sassy import Message


class MessagesInterfaces(_abc.ABC):
    """Message Interface."""

    @_abc.abstractmethod
    def msg(self, name: str, extra: str) -> Message:
        """
        Read a message.

        Args:
            name: The message name.
            extra: More information.

        Returns:
            A Message DTO
        """
        raise NotImplementedError
