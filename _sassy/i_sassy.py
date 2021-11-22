"""Interface for messages."""
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
