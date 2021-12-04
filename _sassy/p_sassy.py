"""
Service for Sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import logging
import os
import typing as _t

import git
import yaml
from colorlog import ColoredFormatter

from _sassy.d_sassy import Message
from _sassy.i_sassy import LoggerInterface, MessagesInterface, RepoInterface

_MESSAGES_FILE = 'messages.yml'
_PATH = os.path.dirname(os.path.abspath(__file__))


class Logger(LoggerInterface):
    """Event logger class."""

    def __init__(self, verbose: bool):
        """
        Init Logger.

        Args:
            verbose: Active verbose
        """
        self.verbose = verbose
        self.LOG_LEVEL = logging.DEBUG
        self.LOG_FORMAT = "%(log_color)s%(asctime)s %(levelname)-" \
                          "8s%(reset)s %(log_color)s%(message)s%(reset)s"

        logging.root.setLevel(self.LOG_LEVEL)
        self.formatter = ColoredFormatter(self.LOG_FORMAT)
        self.stream = logging.StreamHandler()
        self.stream.setLevel(self.LOG_LEVEL)
        self.stream.setFormatter(self.formatter)
        self.log = logging.getLogger('pythonConfig')
        self.log.setLevel(self.LOG_LEVEL)
        self.log.addHandler(self.stream)

    def show(self, message: Message):
        """
        Log the event based on ``Message`` class.

        The method ``Message.level()`` returns the event level as follow:

            - 10 debug
            - 20 info
            - 30 warning
            - 40 error
            - 50 critical

        The attribute ``Message.text`` provide the even message.

        Args:
            message (Message): A ``Message`` DTO

        """
        if self.verbose:
            if message.level() == 10:
                self.log.debug(message.text)
            elif message.level() == 20:
                self.log.info(message.text)
            elif message.level() == 30:
                self.log.warning(message.text)
            elif message.level() == 40:
                self.log.error(message.text)
            elif message.level() == 50:
                self.log.critical(message.text)


class MessageService(MessagesInterface):
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

        message = Message(code=code, severity=severity)
        message.extra = extra
        message.text = text

        return message


class RepoProvider(RepoInterface):
    """``RepoProvider`` class."""

    _INIT_COMMIT = 'Initial commit.'

    @staticmethod
    def _git_add(
            repo: git.repo.base.Repo,
            items: _t.List[str],
    ) -> _t.List[tuple]:
        """
        Initialize a new repository.

        Args:
            repo: A repository.
            items: List of files or directories to add

        Returns (list[tuple]):
            The files and directories added
        """
        try:
            return repo.index.add(items)

        except Exception:
            raise

    def _git_commit(self, repo: git.repo.base.Repo) -> str:
        """
        Initialize a new repository.

        Args:
            repo: A repository.

        Returns:
            The commit number.
        """
        try:
            commit = repo.index.commit(self._INIT_COMMIT)
            return str(commit)

        except Exception:
            raise

    @staticmethod
    def _git_init(repo_dir: str) -> git.repo.base.Repo:
        """
        Initialize a new repository.

        Args:
            repo_dir: A directory name.

        Returns (git.repo.base.Repo):
            The ``Repo``.
        """
        try:
            return git.Repo.init(repo_dir)

        except Exception:
            raise

    def init(self, repo_name: str, items: _t.List[str]) -> str:
        """
        Initialize a new repository.

        Args:
            repo_name (str): A repository name.
            items (list[str]): A list of directories and files.

        Returns:
            The commit number.
        """
        try:
            repo: git.repo.base.Repo = self._git_init(repo_dir=repo_name)
            self._git_add(repo=repo, items=items)
            commit = self._git_commit(repo=repo)
            return str(commit)

        except Exception:
            raise
