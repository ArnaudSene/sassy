"""
Interface for messages.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import abc as _abc
import typing as _t

from _sassy.d_sassy import Message


class LoggerInterface(_abc.ABC):
    """LoggerInterface abstract class (Interface)."""

    @_abc.abstractmethod
    def __init__(self, verbose: bool):
        """
        Init Logger.

        Args:
            verbose: Active verbose
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def show(self, message: Message):
        """
        Show logging.

        Args:
            message: A ``Message`` :abbr:`DTO (Data Transfer Object)`.

        Returns (None):
            None
        """
        raise NotImplementedError


class MessagesInterface(_abc.ABC):
    """Message abstract class (Interface)."""

    @_abc.abstractmethod
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
        raise NotImplementedError


class RepoInterface(_abc.ABC):
    """Repository abstract class (Interface)."""

    @_abc.abstractmethod
    def init(self, repo_name: str, items: _t.List[str]) -> str:
        """
        Initialize a repository.

        Args:
            repo_name (str): A repository name.
            items (list[str]): A list of directories and files.

        Returns:
            None
        """
        raise NotImplementedError
