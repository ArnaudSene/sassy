"""
Sassy application.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import functools
import os
import pathlib
import typing as _t

import yaml as _yaml
from yaml.parser import ParserError

from _sassy import logger_provider
from _sassy.d_sassy import Result, Struct, File, Message
from _sassy.i_sassy import LoggerInterface, RepoInterface, MessagesInterface


class MessageLogger:
    """Log messages as decorator."""

    def __init__(
            self,
            logger: LoggerInterface,
            show: str = 'all'
    ):
        """
        Init the ``MessageLogger``.

        Args:
            logger: The logger provider.
            show: Choose what to log. Choices are: [ok, err, all] default: all
        """
        self.logger = logger
        self.show = show

    def __call__(self, func):
        """
        Log messages.

        Args:
            func: The function decorated.

        Returns (func):
            the function decorated.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result: Result = func(*args, **kwargs)

            if not isinstance(result, Result):
                return result

            if isinstance(result.ok, Message) \
                    and self.show in ['ok', 'all']:
                self.logger.show(message=result.ok)
            elif isinstance(result.err, Message) \
                    and self.show in ['err', 'all']:
                self.logger.show(message=result.err)

            return result

        return wrapper


class Config:
    """``Config`` class."""

    def __init__(
            self,
            message: MessagesInterface
    ):
        """Init ``Config`` instance."""
        self.message = message
        self.cfg = {}

    @MessageLogger(logger_provider, show='err')
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
                result.ok = _yaml.load(file, Loader=_yaml.Loader)
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

    _PATH = pathlib.Path(__file__).parents[0]
    _ROOT_PATH = pathlib.Path(__file__).parents[1]
    _CONFIG_FILE = 'sassy.yml'
    _STRUCTURE = 'structure'
    _FEATURE = 'features'
    _ROOT_DIRS = ['root', 'tests', 'docs']
    _TEST = 'test'
    _DIRS = 'dirs'
    _FILES = 'files'
    _APPS = 'apps'
    _FEAT = 'feature'

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
        self.apps_path = os.path.abspath(self._ROOT_PATH / self.apps)
        self.config_file = os.path.abspath(self._PATH / self._CONFIG_FILE)
        self.update: bool = False
        self.message = message
        self.repo = repo
        super().__init__(message=message)
        super().load_config(config_file=self.config_file)

    def build_path(self, struct_name: str, dir_name: str) -> str:
        """
        Build a path based on structure name and a directory name.

        Args:
            struct_name (str): A structure name e.i: `clean_arch`.
            dir_name (str): A directory name e.i: `applications`.

        Returns (str):
            A path.
        """
        apps = self.apps.replace('-', '_')
        apps_path = pathlib.Path(self.apps_path)
        path = apps_path / apps / dir_name

        if struct_name in self._ROOT_DIRS:
            path = apps_path / dir_name

        return os.path.abspath(path)

    @staticmethod
    def _get_file_dto(
            files: _t.Union[_t.Dict[str, _t.Any], str]
    ) -> _t.Optional[File]:
        """
        Get a ``File`` :abbr:`DTO (Data Transfer Object)`.

        Args:
            files (Union[str, dict]): A file structure.

        Returns (File):
            A ``File`` :abbr:`DTO (Data Transfer Object)`.
        """
        if isinstance(files, str):
            return File(name=files)
        elif isinstance(files, dict):
            for f, c in files.items():
                return File(name=f, content=c)

    def _get_struct_dto(self) -> _t.List[Struct]:
        """
        Get the structure dataset.

        Returns (list[Struct]):
            A list of ``Struct`` :abbr:`DTO (Data Transfer Object)`.
        """
        s = self.cfg[self._STRUCTURE] if self._STRUCTURE in self.cfg else {}
        dto = []

        for k, v in s.items():
            dirs = v[self._DIRS] if self._DIRS in v else []
            files = v[self._FILES] if self._FILES in v else []
            files_dto = [self._get_file_dto(f) for f in files]

            dto.append(Struct(name=k, dirs=dirs, files=files_dto))
        return dto

    def _get_feature_structure_dto(self) -> _t.List[Struct]:
        """
            Get the feature structure dataset.

        Returns (list[Struct]):
            A list of `Struct` :abbr:`DTO (Data Transfer Object)`.
        """
        s = self._get_struct_dto()
        f = self.cfg[self._FEATURE] if self._FEATURE in self.cfg else {}
        feats = []

        for k, v in f.items():
            d = v[self._DIRS] if self._DIRS in v else []
            dirs = []
            for struct in s:
                if struct.name in d:
                    dirs = struct.dirs
                    break

            files = v[self._FILES] if self._FILES in v else []
            files_dto = [self._get_file_dto(f) for f in files]

            feats.append(Struct(name=k, dirs=dirs, files=files_dto))

        return feats

    def create_structure(self) -> Result:
        """
        Create a clean architecture structure.

        Returns (List[str]):
            The list of directories created.
        """
        apps_keyword = {self.cfg[self._APPS]: self.apps}
        repo_name = None
        dirs_and_files = []

        for struct in self._get_struct_dto():
            # create dir
            dirs = struct.dirs if struct.dirs else ['']

            for dir_name in dirs:
                path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)

                result: Result = self.create_dir(name=path)
                if result.err:
                    return result

                if not repo_name:
                    repo_name = path
                else:
                    dirs_and_files.append(path)

                # create file
                for file in struct.files:
                    file_name = file.replace_file_name(apps_keyword)
                    content = file.replace_content(apps_keyword)
                    file_path = os.path.abspath(pathlib.Path(path) / file_name)
                    files = {file_path: content}
                    dirs_and_files.append(file_path)

                    self.create_file(files=files)

        if repo_name:
            repo_apps = InitRepo(repo=self.repo, message=self.message)
            repo_apps(repo_name=repo_name, items=dirs_and_files)

    def create_feature(self, feature: str) -> None:
        """
        Create a clean architecture feature structure.

        Args:
            feature (str): A feature name.

        Returns:
            None
        """
        feature = feature.lower().replace('-', '_')
        feat_keyword = {self.cfg[self._FEAT]: feature}

        for struct in self._get_feature_structure_dto():
            for dir_name in struct.dirs:
                path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)

                # create file
                for file in struct.files:
                    file_name = file.replace_file_name(feat_keyword)
                    content = file.replace_content(feat_keyword)
                    file_path = os.path.abspath(pathlib.Path(path) / file_name)
                    files = {file_path: content}

                    self.create_file(files=files)

    def delete_feature(self, feature: str) -> None:
        """
        Delete a clean architecture feature structure.

        Args:
            feature (str): A feature name.

        Returns:
            None
        """
        payload = {self.cfg[self._FEAT]: feature}

        for struct in self._get_feature_structure_dto():
            for dir_name in struct.dirs:
                path = self.build_path(
                    struct_name=struct.name, dir_name=dir_name)

                # create file
                for file in struct.files:
                    file_name = file.replace_file_name(payload)
                    file_path = os.path.abspath(pathlib.Path(path) / file_name)
                    self.delete_file(file=file_path)

    @MessageLogger(logger=logger_provider, show='all')
    def create_file(
            self,
            files: _t.Dict[str, _t.Any],
    ) -> Result:
        """
        Create a file and add content.

        Args:
            files: A file name

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        for file, content in files.items():

            if os.path.isfile(file) and not self.update:
                result.err = self.message.msg(name='file_exists', extra=file)
                return result

            try:
                with open(file, 'w') as f:
                    if content:
                        f.write(content + "\n")

                result.ok = self.message.msg(name='file_create_ok', extra=file)

            except Exception as exc:
                result.err = self.message.msg(
                    name='file_create_failed', extra=file)
                result.err.text += f" {exc}"

            return result

    @MessageLogger(logger=logger_provider, show='all')
    def delete_file(
            self,
            file: str,
    ) -> Result:
        """
        Delete a file.

        Args:
            file: The file name

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        if not os.path.isfile(file):
            result.err = self.message.msg(name='file_not_exist', extra=file)
            return result

        try:
            os.remove(file)

            result.ok = self.message.msg(name='file_delete_ok', extra=file)

        except Exception as exc:
            result.err = self.message.msg(
                name='file_delete_failed', extra=file)
            result.err.text += f" {exc}"

        return result

    @MessageLogger(logger=logger_provider, show='all')
    def create_dir(self, name: _t.Optional[str] = None) -> Result:
        """
        Create a directory.

        Args:
            name: A directory name.

        Returns:
            Result :abbr:`DTO (Data Transfer Object)`.
              - ok, `Message` :abbr:`DTO (Data Transfer Object)`.
              - err, `Message` :abbr:`DTO (Data Transfer Object)`.
        """
        result = Result()

        if not name:
            name = self.apps_path

        if os.path.isdir(name) and not self.update:
            result.err = self.message.msg(name='dir_exists', extra=name)
            return result

        try:
            os.makedirs(name=name)
        except OSError:
            result.err = self.message.msg(name='dir_create_failed', extra=name)
        else:
            result.ok = self.message.msg(name='dir_create_ok', extra=name)

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

    @MessageLogger(logger=logger_provider, show='all')
    def __call__(self, repo_name: str, items: _t.List[str]) -> Result:
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
            # Check if repo already init

            # init repo
            commit: str = self.repo.init(repo_name=repo_name, items=items)

            result.ok = self.message.msg(name='repo_init_ok', extra=repo_name)
            result.ok.text += f" commit {commit}"

        except Exception as exc:
            result.err = self.message.msg(
                name='repo_init_failed', extra=repo_name)
            result.err.text += f" {exc}"

        return result
