"""
Sassy application.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import functools
import os
import typing as _t
import logging
from colorlog import ColoredFormatter
import yaml as _yaml
from yaml.parser import ParserError

from _sassy import d_sassy as _d, i_sassy as _i

_VERBOSE = os.environ['VERBOSE'] if 'VERBOSE' in os.environ else None


class Logger:
    """Logger provider."""

    LOG_LEVEL = logging.DEBUG
    LOGFORMAT = "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s " \
                "%(log_color)s%(message)s%(reset)s"
    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOGFORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    log = logging.getLogger('pythonConfig')
    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)

    def show(self, message: _d.Message):
        """Show message with logging."""
        if message.level() == 10:
            self.log.debug(message)
        elif message.level() == 20:
            self.log.info(message)
        elif message.level() == 30:
            self.log.warning(message)
        elif message.level() == 40:
            self.log.error(message)
        elif message.level() == 50:
            self.log.critical(message)


def printer(_func=None, *, verbose=None, show=None):
    """Log message information."""

    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            logger = Logger()
            if verbose and show == 'err' and r.err:
                logger.show(message=r.err)
            elif verbose and show == 'ok' and r.ok:
                logger.show(message=r.ok)
            elif verbose and show == 'all':
                if r.ok:
                    logger.show(message=r.ok)
                else:
                    logger.show(message=r.err)
            return r
        return wrapper

    if _func is None:
        return inner
    else:
        return inner(_func)


class Config:
    """Class for config."""

    def __init__(
            self,
            message: _i.MessagesInterfaces
    ):
        """Init Config."""
        self.message = message

    @printer(show='err', verbose=_VERBOSE)
    def load_config(self, config_file) -> _d.Result:
        """
        Load the configuration dataset.

        Returns:
            Result DTO
              - ok, Dict
              - err, Message DTO

        """
        result = _d.Result()

        try:
            with open(config_file) as file:
                result.ok = _yaml.load(file, Loader=_yaml.Loader)

        except FileNotFoundError as exc:
            result.err = self.message.msg(
                name='yaml_file_not_found', extra=f"{exc}")

        except ParserError as exc:
            result.err = self.message.msg(
                name='bad_yaml_format', extra=f"{exc}")

        return result


class Sassy(Config):
    """Mains Sassy class."""

    _PATH = os.path.dirname(os.path.abspath(__file__))
    _ROOT_PATH = "/".join(_PATH.split('/')[:-1])
    _CONFIG_FILE = 'sassy.yml'
    _STRUCTURE = 'structure'
    _FEATURE = 'features'
    _CLARC_STRUCTURE = 'clean_arch'
    _CLARC_TESTS = 'tests'
    _CLARC_CONTENT = 'content'
    _DIRS = 'dirs'
    _FILES = 'files'
    _APPS = 'apps'
    _FEAT = 'feature'

    def __init__(
            self,
            apps: str,
            message: _i.MessagesInterfaces
    ):
        """Init Sassy."""
        super().__init__(message=message)
        self.apps = apps
        self.apps_path = "/".join([self._ROOT_PATH, self.apps])
        self.config_file = "/".join([self._PATH, self._CONFIG_FILE])
        self.update: bool = False
        self.message = message
        self.cfg: _t.Dict[str, _t.Any] = \
            super().load_config(config_file=self.config_file).ok

    @staticmethod
    def _get_file_dto(
            files: _t.Union[_t.Dict[str, _t.Any], str]
    ) -> _t.Optional[_d.File]:
        """
        Get a file DTO.

        Args:
            files: A file as a str or dict

        Returns:
            A File DTO.
        """
        if isinstance(files, str):
            return _d.File(name=files)
        elif isinstance(files, dict):
            for f, c in files.items():
                return _d.File(name=f, content=c)

    def _get_struct_dto(self) -> _t.List[_d.Struct]:
        """
        Get the structure dataset.

        Returns:
            A list of Struct DTO
        """
        s = self.cfg[self._STRUCTURE] if self._STRUCTURE in self.cfg else {}
        dto = []

        for k, v in s.items():
            dirs = v[self._DIRS] if self._DIRS in v else []
            files = v[self._FILES] if self._FILES in v else []
            files_dto = [self._get_file_dto(f) for f in files]

            dto.append(_d.Struct(name=k, dirs=dirs, files=files_dto))
        return dto

    def _get_feature_structure_dto(self) -> _t.List[_d.Struct]:
        """
            Get the feature structure dataset.

        Returns:
            A list of Struct DTO
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

            feats.append(_d.Struct(name=k, dirs=dirs, files=files_dto))
        return feats

    def create_structure(self):
        """Create the clean architecture structure."""
        payload = {self.cfg[self._APPS]: self.apps}

        for struct in self._get_struct_dto():
            # create dir
            dirs = struct.dirs if struct.dirs else ['/']

            for dir_name in dirs:
                path = self.apps_path
                if not dir_name == '/':
                    path = "/".join([self.apps_path, dir_name])

                self.create_dir(name=path)

                # create file
                for file in struct.files:
                    file_name = file.replace_file_name(payload)
                    content = file.replace_content(payload)
                    file_path = "/".join([path, file_name])
                    files = {file_path: content}

                    self.create_file(files=files)

    def create_feature(self, feature: str):
        """Create the clean architecture features structure."""
        payload = {self.cfg[self._FEAT]: feature}

        for struct in self._get_feature_structure_dto():
            for dir_name in struct.dirs:
                path = "/".join([self.apps_path, dir_name])

                # create file
                for file in struct.files:
                    file_name = file.replace_file_name(payload)
                    content = file.replace_content(payload)
                    file_path = "/".join([path, file_name])
                    files = {file_path: content}

                    self.create_file(files=files)

    @printer(show='all', verbose=_VERBOSE)
    def create_file(
            self,
            files: _t.Dict[str, _t.Any],
    ) -> _d.Result:
        """
        Create file and add content.

        Args:
            files: The file name

        Returns:
            Result DTO
              - ok, Message DTO
              - err, Message DTO
        """
        result = _d.Result()

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

    @printer(show='all', verbose=_VERBOSE)
    def create_dir(self, name: _t.Optional[str] = None) -> _d.Result:
        """
        Create directory.

        Args:
            name: The directory name.

        Returns:
            Result DTO
              - ok, Message DTO
              - err, Message DTO
        """
        result = _d.Result()

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
