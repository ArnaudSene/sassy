"""
Sassy tool.

A tool to manage project based on a clean architecture structure.

This file is built under a clean architecture structure with:
 - Domains/Entities
 - Interfaces/Abstract classes
 - Applications/Business Logic
 - Providers/Services

Features:
 - Create a clean architecture structure based on YAML configuration file.
 - Init a Git repository
 - Create a feature
 - Delete a feature

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import logging
import logging.config
from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from os.path import abspath
from pathlib import Path
from typing import Optional, Any, Dict, Union, List

from git import BaseIndexEntry, Repo
from yaml import load, Loader
from yaml.parser import ParserError

PATH = Path(__file__).parent
UPPER_PATH = PATH.parent
ROOT_PATH = Path('.')

MESSAGES_FILE = PATH / 'messages.yml'
LOG_CONF_FILE = "logging_default.yml"
CONFIG_FILE = 'sassy.yml'
LOGGER = 'root'


def get_version() -> str:
    """
    Get the version number from VERSION.

    Returns (str):
        The version number
    """
    with open(UPPER_PATH / 'VERSION', 'r') as f:
        return f.read()


@dataclass
class Result:
    """Result :abbr:`DTO (Data Transfer Object)`."""

    _ok: Optional[str] = None
    _err: Optional[str] = None

    def __str__(self) -> str:
        """
        Rewrite ``Result`` as a string.

        Used with ``str(instance)`` or ``format`` function.

        Returns (str):
            ok | err as a string.
        """
        if self.ok:
            return f'{self.ok}'
        else:
            return f'{self.err}'

    @property
    def ok(self) -> Any:
        """
        Get ok.

        :getter: Returns the ok value.
        :setter: Sets the ok value.
        :type: Any

        Returns (Any):
            ok result.
        """
        return self._ok

    @ok.setter
    def ok(self, val: Any):
        """
        Set ok.

        Args:
            val (Any): A value.
        """
        if val:
            self._ok = val
            self._err = None

    @property
    def err(self) -> Any:
        """
        Get error.

        :getter: Returns the err value.
        :setter: Sets the err value.
        :type: Any

        Returns (Any):
            An error.
        """
        return self._err

    @err.setter
    def err(self, val: Any):
        """
        Set error.

        Args:
            val (Any): A value.
        """
        if val:
            self._err = val
            self._ok = None


@dataclass
class Message:
    """``Message`` :abbr:`DTO (Data Transfer Object)`."""

    code: int
    severity: str
    _text: str = ""
    extra: Optional[str] = None

    class SeverityLevel(Enum):
        """Severity levels."""

        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

    def __repr__(self) -> str:
        """
        ``Message`` machine-readable.

        Use with ``repr(instance)`` function.

        Returns (str):
            Message(code: <code>, severity: <severity>, text: <text>)
        """
        return f"{self.__class__.__name__}" \
               f"(code: {self.code}, severity: {self.severity}, " \
               f"text: {self.text})"

    def __str__(self) -> str:
        """
        ``Message`` human-readable.

        Use with ``str(instance)`` or ``format`` functions.

        Returns (str):
            (<code>, <severity>, <text>)
        """
        return f"({self.code},{self.severity},{self.text})"

    def as_dict(self) -> Dict[str, Any]:
        """
        Convert ``Message`` into a dict.

        Returns (dict[str, Any]):
            ``Message`` as a dict.
        """
        return {
            "code": self.code,
            "severity": self.severity,
            "text": self.text
        }

    @property
    def text(self) -> str:
        """
        Get text value.

        :getter: Returns the text value.
        :setter: Sets the text value.
        :type: str

        Returns (str):
            A text.
        """
        return self._text

    @text.setter
    def text(self, text: str):
        """
        Set text value.

        :getter: Returns the text value.
        :setter: Sets the text value.
        :type: str

        Args:
            text (str): A text.
        """
        self._text = text.replace("'{}' ", "")

        if self.extra:
            self._text = text.format(self.extra)

    def level(self):
        """
        Get the severity level.

        Returns (str):
            The level name.
        """
        if self.severity in self.SeverityLevel.__members__:
            return self.SeverityLevel[self.severity].value
        return self.SeverityLevel['INFO'].value


@dataclass
class File:
    """``File`` :abbr:`DTO (Data Transfer Object)`."""

    name: str
    content: str = ''

    def replace_content(self, payload: Dict[str, Any]) -> str:
        """
        Rename a content file.

        Args:
            payload: A key, value that represent what needs to be replaced
                    and by which value.
                    key: The key that needs to be replaced
                    value: The value that will be apply

        Returns (str):
            The content with string replaced.
        """
        if self.content:
            for k, v in payload.items():
                self.content = self.content.replace(k, v)

        return self.content

    def replace_file_name(self, payload: Dict[str, Any]) -> str:
        """
        Replace the file name.

        Args:
            payload: A key, value that represent what needs to be replaced \
                    and by which value.
                    **key**: The key that needs to be replaced.
                    **value**: The value that will be apply.

        Returns (str):
            The file name.
        """
        if self.name:
            for k, v in payload.items():
                self.name = self.name.replace(k, v)

        return self.name


@dataclass
class Struct:
    """Struct :abbr:`DTO (Data Transfer Object)`."""

    name: str
    dirs: List[Any]
    files: List[File]


class MessagesInterface(ABC):
    """Message abstract class (Interface)."""

    @abstractmethod
    def msg(self, name: str, extra: Optional[str] = None) -> Message:
        """
        Read a message.

        Args:
            name (str): The message name.
            extra (Optional[str]): Extra information.

        Returns (Message):
            A ``Message`` :abbr:`DTO (Data Transfer Object)`.
        """
        raise NotImplementedError


class RepoInterface(ABC):
    """Repository abstract class (Interface)."""

    @abstractmethod
    def init(self, repo_name: str, items: List[str]) -> str:
        """
        Initialize a repository.

        Args:
            repo_name (str): A repository name.
            items (list[str]): A list of directories and files.

        Returns:
            None
        """
        raise NotImplementedError


class MessageService(MessagesInterface):
    """Message Service class."""

    def __init__(self):
        """Init instance."""
        self.messages: Dict[str, Any] = {}
        self.message_file = MESSAGES_FILE
        self.load_messages()

    def load_messages(self):
        """Set messages."""
        if not self.messages:
            with open(self.message_file) as file:
                self.messages = load(file, Loader=Loader)

    def msg(self, name: str, extra: Optional[str] = None) -> Message:
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
            repo: Repo,
            items: List[str]
    ) -> List[BaseIndexEntry]:
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

    def _git_commit(self, repo: Repo) -> str:
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
    def _git_init(repo_dir: str) -> Repo:
        """
        Initialize a new repository.

        Args:
            repo_dir: A directory name.

        Returns (git.repo.base.Repo):
            The ``Repo``.
        """
        try:
            return Repo.init(repo_dir)

        except Exception:
            raise

    def init(self, repo_name: str, items: List[str]) -> str:
        """
        Initialize a new repository.

        Args:
            repo_name (str): A repository name.
            items (list[str]): A list of directories and files.

        Returns:
            The commit number.
        """
        try:
            repo: Repo = self._git_init(repo_dir=repo_name)
            self._git_add(repo=repo, items=items)
            commit = self._git_commit(repo=repo)

            return str(commit)

        except Exception:
            raise


class MessageLogger:
    """Logger as decorator."""

    def __init__(self, show: str = 'all'):
        """
        Init Logger.

        Args:
            show (str): Choose what to log.
                Choices are: [ok, err, all] default: all
        """
        self.show = show
        self.logging_conf = PATH / LOG_CONF_FILE

        with open(self.logging_conf, 'r') as f:
            logging_config = load(f, Loader=Loader)
            logging.config.dictConfig(logging_config)

        self.logger = logging.getLogger(LOGGER)

    def __call__(self, func):
        """
        Log messages.

        Args:
            func: The function decorated.

        Returns (func):
            the function decorated.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            result: Result = func(*args, **kwargs)

            if self.show == 'debug':
                m = Message(code=1, severity='DEBUG')
                m.text = f"{func.__name__}:{result}"
                self.log(message=m)

            if not isinstance(result, Result):
                return result

            if isinstance(result.ok, Message) \
                    and self.show in ['ok', 'all']:
                result.ok.text = result.ok.text
                self.log(message=result.ok)

            elif isinstance(result.err, Message) \
                    and self.show in ['err', 'all']:
                result.err.text = result.err.text
                self.log(message=result.err)

            return result

        return wrapper

    def log(self, message: Message):
        """
        Log messages.

        Args:
            message: ``Message`` DTO

        Returns:
            None
        """
        if message.level() == 10:
            self.logger.debug(message.text)
        elif message.level() == 20:
            self.logger.info(message.text)
        elif message.level() == 30:
            self.logger.warning(message.text)
        elif message.level() == 40:
            self.logger.error(message.text)
        elif message.level() == 50:
            self.logger.critical(message.text)


class Config:
    """``Config`` class."""

    def __init__(self, message: MessagesInterface):
        """Init ``Config`` instance."""
        self.message = message
        self.cfg: Dict[str, Any] = {}

    @MessageLogger(show='err')
    def load_config(self, config_file) -> Result:
        """
        Load the configuration dataset.

        Returns (Result):
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, (dict) A dataset.
              - err, Message :abbr:`DTO (Data Transfer Object)`.

        """
        result = Result()

        try:
            with open(config_file) as file:
                result.ok = load(file, Loader=Loader)
                self.cfg = result.ok

        except FileNotFoundError as exc:
            result.err = self.message.msg(
                name='yaml_file_not_found', extra=f"{exc}")

        except ParserError as exc:
            result.err = self.message.msg(
                name='bad_yaml_format', extra=f"{exc}")

        return result


class Sassy(Config):
    """``Sassy`` class."""

    STRUCTURE = 'structure'
    FEATURE = 'features'
    ROOT_DIRS = ['root', 'tests', 'docs']
    TEST = 'test'
    DIRS = 'dirs'
    FILES = 'files'
    APPS = 'apps'
    FEAT = 'feature'
    ARGS = 'args'

    def __init__(
            self,
            apps: str,
            message: MessagesInterface,
            repo: RepoInterface
    ):
        """
        Init ``Sassy`` instance.

        Args:
            apps (str): An application name.
            message (MessagesInterfaces): A message provider
                (dependency injection).
        """
        self.apps = apps
        self.apps_path: Path = ROOT_PATH / self.apps
        self.config_file: Path = PATH / CONFIG_FILE
        self.update: bool = False
        self.message = message
        self.repo = repo
        super().__init__(message=message)
        super().load_config(config_file=self.config_file)

    def build_path(self, struct_name: str, dir_name: str) -> Path:
        """
        Build a path based on structure name and a directory name.

        Args:
            struct_name (str): A structure name e.i: `clean_arch`.
            dir_name (str): A directory name e.i: `applications`.

        Returns (Path):
            A path.
        """
        sub_dir = 'src'
        path = self.apps_path / sub_dir / dir_name

        if struct_name in self.ROOT_DIRS:
            path = self.apps_path / dir_name

        return path

    @staticmethod
    def _get_file_dto(files: Union[Dict[str, Any], str]) -> File:
        """
        Get a ``File`` :abbr:`DTO (Data Transfer Object)`.

        Args:
            files (Union[str, dict]): A file structure.

        Returns (File):
            A ``File`` :abbr:`DTO (Data Transfer Object)`.
        """
        # Only a file name
        if isinstance(files, str):
            return File(name=files)

        # A file name and his content
        if isinstance(files, dict):
            for f, c in files.items():
                return File(name=f, content=c)

    def _get_args(self) -> Dict[str, str]:
        """
        Get args dataset.

        Returns (dict):
            A dict of args
        """
        return self.cfg.get(self.ARGS, {})

    def _get_struct_dto(self, field: str = STRUCTURE) -> List[Struct]:
        """
        Get a structure dataset.

        Args:
            field: The field to extract the structure

        Returns (list[Struct]):
            A list of ``Struct`` :abbr:`DTO (Data Transfer Object)`.
        """
        structures: Dict[str, Any] = self.cfg.get(field, {})
        dto = []

        for k, v in structures.items():
            dirs: List[str] = v.get(self.DIRS, [])
            files: List[str] = v.get(self.FILES, [])
            files_dto: List[File] = [self._get_file_dto(f) for f in files]
            dto.append(Struct(name=k, dirs=dirs, files=files_dto))

        return dto

    def _get_feature_structure_dto(self) -> List[Struct]:
        """
        Get the feature structure dataset.

        Returns (list[Struct]):
            A list of `Struct` :abbr:`DTO (Data Transfer Object)`.
        """
        feature_structures = []
        structs: List[Struct] = self._get_struct_dto()
        features: List[Struct] = self._get_struct_dto(field=self.FEATURE)

        for feat_struct in features:
            feat_directories: List[str] = feat_struct.dirs
            feat_files: List[File] = feat_struct.files

            dirs = []
            for struct in structs:
                if struct.name in feat_directories:
                    dirs = struct.dirs
                    break

            feature_structures.append(
                Struct(name=feat_struct.name, dirs=dirs, files=feat_files))
        return feature_structures

    def create_structure(self) -> Result:
        """
        Create a clean architecture structure.

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        apps_keyword = {self.cfg[self.APPS]: self.apps}
        repo_path_name: Optional[Path] = None
        dirs_and_files = []

        for struct in self._get_struct_dto():
            # create dir
            dirs = struct.dirs if struct.dirs else ['']

            for dir_name in dirs:
                path: Path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)

                result: Result = self.create_dir(name=path)
                if result.err:
                    return result

                if not repo_path_name:
                    repo_path_name = path
                else:
                    dirs_and_files.append(path)

                # create file
                for file in struct.files:
                    file_name: str = file.replace_file_name(apps_keyword)
                    content: str = file.replace_content(apps_keyword)
                    file_path: Path = path / file_name
                    files = {file_path: content}
                    dirs_and_files.append(file_path)

                    self.create_file(files=files)

        if repo_path_name:
            repo_name: str = abspath(repo_path_name)
            items: List[str] = [abspath(d) for d in dirs_and_files]
            repo_apps = InitRepo(repo=self.repo, message=self.message)
            repo_apps(repo_name=repo_name, items=items)

    def is_valid_directory(
            self,
            directory: str,
            directories: Optional[List[str]] = None
    ) -> bool:
        """
        Check if directory exist in directories. This method returns True \
        if directory is in directories.

        Args:
            directory (str): The directory to handle
            directories (list): Directories used as filter

        Returns (bool):
        """
        if directories is None or not directories:
            return True

        for dirname in directories:
            if dirname.startswith('*'):
                args = self._get_args()
                dirname = args.get(dirname, 'invalid')

            if directory.endswith(dirname):
                return True
        return False

    def create_feature(self, feature: str, **kwargs) -> None:
        """
        Create a clean architecture feature structure.

        Args:
            feature (str): A feature name.
            kwargs (dict): must be a dict like:

            ```
                {"directories": ['dirname_a']}
            ```

        Returns:
            None
        """
        feature = feature.lower().replace('-', '_')
        feat_keyword = {self.cfg[self.FEAT]: feature}

        for struct in self._get_feature_structure_dto():
            for dir_name in struct.dirs:
                if not self.is_valid_directory(directory=dir_name, **kwargs):
                    continue

                path: Path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)
                # create file
                for file in struct.files:
                    file_name: str = file.replace_file_name(feat_keyword)
                    content: str = file.replace_content(feat_keyword)
                    file_path: Path = path / file_name
                    files = {file_path: content}

                    self.create_file(files=files)

    def delete_feature(self, feature: str, **kwargs) -> None:
        """
        Delete a clean architecture feature structure.

        Args:
            feature (str): A feature name.
            kwargs (dict): must be a dict like:

            ```
                {"directories": ['dirname_a']}
            ```

        Returns:
            None
        """
        payload = {self.cfg[self.FEAT]: feature}

        for struct in self._get_feature_structure_dto():
            for dir_name in struct.dirs:
                if not self.is_valid_directory(directory=dir_name, **kwargs):
                    continue

                path: Path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)

                # create file
                for file in struct.files:
                    file_name: str = file.replace_file_name(payload)
                    file_path: Path = path / file_name
                    self.delete_file(file=file_path)

    @MessageLogger(show='all')
    def create_file(self, files: Dict[Path, Any]) -> Result:
        """
        Create a file and add content.

        Args:
            files (dict[Path, Any]): A file name

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        for file, content in files.items():
            if file.is_file() and not self.update:
                result.err = self.message.msg(
                    name='file_exists', extra=str(file))
                return result

            try:
                file.touch()
                file.write_text(content + "\n")
                result.ok = self.message.msg(
                    name='file_create_ok', extra=str(file))

            except Exception as exc:
                result.err = self.message.msg(
                    name='file_create_failed', extra=str(file))
                result.err.text += f" {exc}"

            return result

    @MessageLogger(show='all')
    def delete_file(self, file: Path) -> Result:
        """
        Delete a file.

        Args:
            file (Path): The file name

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        if not file.is_file():
            result.err = self.message.msg(
                name='file_not_exist', extra=str(file))
            return result

        try:
            file.unlink()
            result.ok = self.message.msg(
                name='file_delete_ok', extra=str(file))

        except Exception as exc:
            result.err = self.message.msg(
                name='file_delete_failed', extra=str(file))
            result.err.text += f" {exc}"

        return result

    @MessageLogger(show='all')
    def create_dir(self, name: Optional[Path] = None) -> Result:
        """
        Create a directory.

        Args:
            name (Path): A directory name.

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        if not name:
            name = self.apps_path

        if name.is_dir() and not self.update:
            result.err = self.message.msg(name='dir_exists', extra=str(name))
            return result

        try:
            name.mkdir(parents=True)
        except (FileExistsError, FileNotFoundError):
            result.err = self.message.msg(
                name='dir_create_failed', extra=str(name))
        else:
            result.ok = self.message.msg(name='dir_create_ok', extra=str(name))

        return result


class InitRepo:
    """InitRepo class application."""

    def __init__(
            self,
            repo: RepoInterface,
            message: MessagesInterface,
    ):
        """Init RepoProvider."""
        self.message = message
        self.repo = repo

    @MessageLogger(show='all')
    def __call__(self, repo_name: str, items: List[str]) -> Result:
        """
        Init a repository.

        Args:
            repo_name: A repository name.

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()
        try:
            # init repo
            commit: str = self.repo.init(repo_name=repo_name, items=items)
            result.ok = self.message.msg(name='repo_init_ok', extra=repo_name)
            result.ok.text += f" commit {commit}"

        except Exception as exc:
            result.err = self.message.msg(
                name='repo_init_failed', extra=repo_name)
            result.err.text += f" {exc}"

        return result
