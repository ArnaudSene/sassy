"""
Sassy application.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import functools
import os
import typing as _t

import yaml as _yaml
from yaml.parser import ParserError

from _sassy import d_sassy as _d, p_sassy as _p

_VERBOSE = True


def printer(_func=None, *, verbose=False, err=False):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)

            if _VERBOSE and verbose:
                print(f"DEBUG: {r}")
            if _VERBOSE and err and r.err:
                print(f"ERROR: {r.err}")
            return r
        return wrapper

    if _func is None:
        return inner
    else:
        return inner(_func)


class Sassy:
    """Mains Sassy class."""

    _PATH = os.path.dirname(os.path.abspath(__file__))
    _CONFIG_FILE = 'sassy.yml'
    _STRUCTURE = 'structure'
    _DIRS = 'dirs'
    _FILES = 'files'
    _APPS = 'apps'

    def __init__(self, apps: str):
        """Init Sassy."""
        self.apps = apps
        self.apps_path = "/".join([self._PATH, self.apps])
        self.config_file = "/".join([self._PATH, self._CONFIG_FILE])
        self.update: bool = False
        self.result = _d.Result()
        self.message = _p.MessageService()
        self.cfg: _t.Dict[str, _t.Any] = self.load_config().ok

    @printer(err=True)
    def load_config(self) -> _d.Result:
        """
        Load the configuration dataset.

        Returns:
            Result DTO
              - ok, Dict
              - err, Message DTO

        """
        try:
            with open(self.config_file) as file:
                self.result.ok = _yaml.load(file, Loader=_yaml.Loader)

                if self._STRUCTURE not in self.result.ok:
                    self.result.err = self.message.msg(
                        name='yaml_file_kw_missing', extra=self._STRUCTURE)

        except FileNotFoundError as exc:
            self.result.err = self.message.msg(
                name='yaml_file_not_found', extra=f"{exc}")

        except ParserError as exc:
            self.result.err = self.message.msg(
                name='bad_yaml_format', extra=f"{exc}")

        return self.result

    def replace_apps_content(
            self,
            content: str
    ) -> str:
        """
        Replace apps keyword with apps value in content.

        Args:
            content: The content file.

        Returns:
            The content updated
        """
        kw_apps = self.cfg[self._APPS]
        new_content = content.replace(kw_apps, self.apps)
        return new_content

    @staticmethod
    def define_file(file: _t.Any) -> _t.Dict[str, _t.Any]:
        """
        Define the file structure as a dict.

        Args:
            file: The file where file could be a string or a dict.

        Returns:
            A file as a dict.
        """
        files = {}
        if isinstance(file, str):
            files.update({file: ""})

        elif isinstance(file, dict):
            for _file, content in file.items():
                files.update({_file: content})

        return files

    @printer(verbose=True)
    def create_structure(self) -> _d.Result:
        """
        Create structure based on YAML file.

        Returns:
            Result DTO
              - ok, Message DTO
              - err, Message DTO
        """
        self.create_dir()

        for kw_main in self.cfg[self._STRUCTURE].keys():
            self.create_files_and_dirs(kw_main=kw_main)

        self.result.ok = self.message.msg(name='create_structure_ok')
        return self.result

    def create_files_and_dirs(
            self,
            kw_main: str
    ) -> _d.Result:
        """
        Create directories and files for system structure.

        Args:
            kw_main: A keyword as a string

        Returns:
            Result DTO
              - ok, Message DTO
              - err, Message DTO
        """
        kw_main = kw_main
        kw_dirs = self._DIRS
        kw_files = self._FILES

        if kw_main not in self.cfg[self._STRUCTURE]:
            self.result.err = self.message.msg(
                name='no_keyword', extra=kw_main)
            return self.result

        struct_main = self.cfg[self._STRUCTURE][kw_main]

        dirs = struct_main[kw_dirs] if kw_dirs in struct_main else ['root']
        files = struct_main[kw_files] if kw_files in struct_main else []

        for dir_name in dirs:
            if dir_name != 'root':
                self.create_dir(name=dir_name)
            else:
                dir_name = None

            for file in files:
                files = self.define_file(file=file)
                self.create_file(files=files, dir_name=dir_name)

        self.result.ok = self.message.msg(
            name='create_dir_files_ok', extra=kw_main)
        return self.result

    @printer(verbose=True)
    def create_file(
            self,
            files: _t.Dict[str, _t.Any],
            dir_name: _t.Optional[str] = None
    ) -> _d.Result:
        """
        Create file and add content.

        Args:
            files: The file name
            dir_name: The directory

        Returns:
            Result DTO
              - ok, Message DTO
              - err, Message DTO
        """
        path = self.apps_path

        if dir_name:
            path = "/".join([path, dir_name])

        for file, content in files.items():
            file = "/".join([path, file])

            if os.path.isfile(file) and not self.update:
                self.result.err = self.message.msg(
                    name='file_exists', extra=file)
                return self.result

            try:
                with open(file, 'w') as f:
                    if content:
                        updated_content = self.replace_apps_content(
                            content=content)
                        f.write(updated_content + "\n")

                self.result.ok = self.message.msg(
                    name='file_create_ok', extra=file)

            except Exception as exc:
                self.result.err = self.message.msg(
                    name='file_create_failed', extra=file)
                self.result.err.text += f" {exc}"

            return self.result

    @printer(verbose=True)
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
        if name:
            path = "/".join([self.apps_path, name])
        else:
            path = self.apps_path

        if os.path.isdir(path) and not self.update:
            self.result.err = self.message.msg(
                name='dir_exists', extra=path)
            return self.result

        try:
            os.makedirs(name=path)
        except OSError:
            self.result.err = self.message.msg(
                name='dir_create_failed', extra=path)
        else:
            self.result.ok = self.message.msg(
                name='dir_create_ok', extra=path)

        return self.result
