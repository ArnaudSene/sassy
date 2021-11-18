"""Unit test for _sassy."""
import pytest
import _sassy.d_sassy as _d
import sassy as _sassy
import yaml as _yaml
from yaml.parser import ParserError
import os


class TestSassy:
    """Main test for Sassy."""

    sassy = _sassy.Sassy(apps='test_sassy')
    cwd = os.path.dirname(os.path.abspath(__file__))
    yaml_file = "/".join([cwd, 'sassy.yml'])

    def test_sassy_load_config_ok(self):
        """load_config return a dict."""
        result = self.sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.ok

    def test_sassy_load_config_file_not_found(self):
        """load_config raise FileNotFoundError."""
        self.sassy.config_file = 'bad_file'
        result = self.sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.err

    def test_sassy_load_config_bad_format(self):
        """load_config raise ParserError."""
        yaml_file = "/".join([self.cwd, 'test_sassy.py'])
        self.sassy.config_file = yaml_file
        result = self.sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.err

    def test_define_file_file_as_str_ok(self):
        """Define the file format as a dict."""
        file = 'a file'
        expected = {file: ""}
        result = self.sassy.define_file(file=file)
        assert result == expected

    def test_define_file_file_as_dict_ok(self):
        """Define the file format as a dict."""
        file = {'a file': 'content'}
        expected = file
        result = self.sassy.define_file(file=file)
        assert result == expected

    def test_replace_apps_content(self):
        """Replace content with apps"""
        content = '"""Some content with __APPS__."""'
        expected = content.replace('__APPS__', self.sassy.apps)
        new_content = self.sassy.replace_apps_content(content)
        assert new_content == expected

    # def test_create_structure(self):
    #     """"""
    #     print()
    #     self.sassy.create_structure()
