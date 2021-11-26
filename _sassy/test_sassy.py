"""
Unit test for _sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import os
from unittest.mock import patch, mock_open, call

import pytest

import _sassy.a_sassy as _a
import _sassy.d_sassy as _d
import _sassy.p_sassy as _p


class TestSassy:
    """Main test for Sassy."""

    APPS_PATH = '_sassy.a_sassy'
    _a._VERBOSE = False
    cwd = os.path.dirname(os.path.abspath(__file__))
    yaml_file = "/".join([cwd, 'sassy.yml'])
    message = _p.MessageService()

    def test_result_dto_ok_or_err(self):
        """ok or err but not both together."""
        r = _d.Result()
        r.err = 'err'
        r.ok = 'ok'
        assert r.ok
        assert not r.err

    def test_result_dto_as_str_ok(self):
        """rewrite __str__."""
        r = _d.Result()
        r.ok = 'this is a string'

        assert str(r) == 'this is a string'

    def test_result_dto_as_str_err(self):
        """rewrite __str__."""
        r = _d.Result()
        r.err = 'this is an error'

        assert str(r) == 'this is an error'

    @pytest.mark.parametrize('sev, lvl', [
        ('DEBUG', 10),
        ('INFO', 20),
        ('WARNING', 30),
        ('ERROR', 40),
        ('CRITICAL', 50),
        ('invalid', 20),
    ])
    def test_message_dto_severity_level(self, sev, lvl):
        code = 999
        severity = sev
        extra = 'extra'
        m = _d.Message(code, severity, extra)
        assert m.level() == lvl

    def test_message_dto_reps(self):
        """rewrite __repr__."""
        code = 999
        severity = 'TEST'
        extra = 'extra'
        text = 'a fake text'
        expected = f"Message(code: {code}, severity: {severity}, text: {text})"

        m = _d.Message(code, severity, extra)
        m.text = text

        assert repr(m) == expected

    def test_message_dto_as_str(self):
        """rewrite __str__."""
        code = 999
        severity = 'TEST'
        extra = 'extra'
        text = 'a fake text'
        expected = f"({code},{severity},{text})"

        m = _d.Message(code, severity, extra)
        m.text = text

        assert str(m) == expected

    def test_message_dto_as_dict(self):
        """as_dict() method"""
        code = 999
        severity = 'TEST'
        extra = 'extra'
        text = 'a fake text'
        expected = {
            "code": code,
            "severity": severity,
            "text": text
        }

        m = _d.Message(code, severity, extra)
        m.text = text

        assert m.as_dict() == expected

    def test_message_provider(self):
        m = _p.MessageService()
        result = m.msg(name='invalid')
        assert result.code == 300

    def test_sassy_load_config_ok(self):
        """load_config return a dict."""
        config = _a.Config(message=self.message)
        result_cfg = config.load_config(config_file=self.yaml_file)
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        assert result_cfg.ok == sassy.cfg

    def test_sassy_load_config_bad_format(self):
        """load_config raise ParserError."""
        config = _a.Config(message=self.message)
        yaml_file = "/".join([self.cwd, 'test_sassy.py'])
        result = config.load_config(config_file=yaml_file)
        assert result.err.code == 400

    def test_sassy_load_config_file_not_found(self):
        """load_config raise FileNotFoundError."""
        config_file = 'bad_file'
        config = _a.Config(message=self.message)
        result = config.load_config(config_file=config_file)
        assert result.err.code == 401

    @pytest.mark.parametrize('files, expected', [
        ('fake_file', ['fake_file', '']),
        ({
             'fake_file': '"""THis is a content."""'
         }, ['fake_file', '"""THis is a content."""'])
    ])
    def test_get_file_dto_ok(self, files, expected):
        """Get a File DTO."""
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        file: _d.File = sassy._get_file_dto(files=files)
        assert file.name == expected[0]
        assert file.content == expected[1]

    @pytest.mark.parametrize('idx, files', [
        (0, 123),
        (1, True),
        (2, False),
        (3, [123]),
        (4, None),
    ])
    def test_get_file_dto_not_ok(self, idx, files):
        """Get None."""
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        file: _d.File = sassy._get_file_dto(files=files)
        assert file is None

    def test__get_struct_dto_not_ok(self):
        """Invalid yaml file or missing keyword. Result is []"""
        mock_result = _d.Result()
        mock_result.ok = {'kw': 'invalid'}
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        result = sassy._get_struct_dto()
        assert not result
        patcher.stop()

    def test__get_struct_dto_ok(self):
        """Valid yaml file. Result is list of Struct DTO"""
        mock_result = _d.Result()
        mock_result.ok = {
            'structure': {
                'root': {
                    'files': ['fake_file'],
                    'dirs': ['dir_1', 'dir_2']
                }
            }
        }
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        result = sassy._get_struct_dto()
        assert result[0].name == 'root'
        assert result[0].dirs == ['dir_1', 'dir_2']
        assert result[0].files == [_d.File(name='fake_file')]
        patcher.stop()

    def test__get_feature_structure_dto_not_ok(self):
        """Invalid yaml file or missing keyword. Result is []"""
        mock_result = _d.Result()
        mock_result.ok = {'kw': 'invalid'}
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        result = sassy._get_feature_structure_dto()
        assert not result
        patcher.stop()

    def test__get_feature_structure_dto_ok(self):
        """Valid yaml file. Result is list of Struct DTO"""
        mock_result = _d.Result()
        mock_result.ok = {
            'structure': {
                'root': {
                    'files': ['fake_file'],
                    'dirs': ['dir_1', 'dir_2']
                }
            },
            'features': {
                'apps': {
                    'files': ['fake_file.py'],
                    'dirs': ['root']
                }
            }
        }
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        result = sassy._get_feature_structure_dto()
        assert result[0].name == 'apps'
        assert result[0].dirs == ['dir_1', 'dir_2']
        assert result[0].files == [_d.File(name='fake_file.py')]
        patcher.stop()

    def tests_create_dir_already_exist(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{self.APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.err.code == 201

    def tests_create_dir_success(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = False
        makedir_patcher = patch(f'{self.APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.ok.code == 102

    def tests_create_dir_success_already_exist(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = True
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{self.APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.ok.code == 102

    def tests_create_dir_failed_with_os_error_exception(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = True
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{self.APPS_PATH}.os.makedirs')
        mock_makedir = makedir_patcher.start()
        mock_makedir.side_effect = OSError

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.err.code == 302

    def test_create_dir_success_with_params(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        name = 'fake_name'
        sassy.create_dir(name=name)
        mock_isdir.assert_called_once_with(name)
        isdir_patcher.stop()

    def test_create_dir_success_without_params(self):
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        sassy.create_dir()
        mock_isdir.assert_called_once_with(f"{sassy.apps_path}")
        isdir_patcher.stop()

    def test_create_file_already_exist(self):
        """File is already exist"""
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{self.APPS_PATH}.os.path.isfile')
        mock_isfile = patcher.start()
        mock_isfile.return_value = True
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 200
        patcher.stop()

    def test_create_file_success_ok(self):
        """Write file ok"""
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        fake_file = 'fake/file/path/fake_file.py'
        content = "Message to write on file to be written"

        with patch(f'{self.APPS_PATH}.open', mock_open()) as mocked_file:
            r = sassy.create_file(files={fake_file: content})

            mocked_file.assert_called_once_with(f"{fake_file}", 'w')

            mocked_file().write.assert_called_once_with(content + "\n")
            assert r.ok.code == 101

    def test_create_file_failed_raise_exception(self):
        """Raise exception"""
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{self.APPS_PATH}.open')
        mock_open_ = patcher.start()
        mock_open_.side_effect = Exception('fake_error')
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 301
        patcher.stop()

    def test_replace_content_ok(self):
        """replace ok"""
        content = '"""this is a test for __APPS__."""'
        expected = '"""this is a test for replaced_value."""'
        file = _d.File(name='fake', content=content)
        payload = {
            '__APPS__': 'replaced_value',
            'inexist': 'nothing'
        }
        assert file.replace_content(payload) == expected

    def test_replace_content_not_ok(self):
        """Nothing replaced"""
        content = '"""this is a test for __APPS__."""'
        expected = '"""this is a test for __APPS__."""'
        file = _d.File(name='fake', content=content)
        payload = {
            'inexist': 'nothing'
        }
        assert file.replace_content(payload) == expected

    def test_create_structure_ok(self):
        mock_result = _d.Result()
        mock_result.ok = {
            'apps': '__ABC__',
            'feature': '__123__',
            'structure': {
                'root': {
                    'files': ['fake_file'],
                    'dirs': ['dir_1', 'dir_2']
                }
            },
            'features': {
                'apps': {
                    'files': ['fake_file.py'],
                    'dirs': ['root']
                }
            }
        }
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result

        result = _d.Result()
        result.ok = 'this is ok'
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        dir_patcher = patch(f'{self.APPS_PATH}.Sassy.create_dir')
        file_patcher = patch(f'{self.APPS_PATH}.Sassy.create_file')
        mock_create_dir = dir_patcher.start()
        mock_create_dir.return_value = result
        mock_create_file = file_patcher.start()
        mock_create_file.return_value = result

        sassy.create_structure()
        dir_calls = [
            call(name='/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_1'),
            call(name='/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_2')
        ]
        mock_create_dir.assert_has_calls(dir_calls, any_order=True)

        file_calls = [
            call(files={'/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_1/'
                        'fake_file': ''}),
            call(files={'/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_2/'
                        'fake_file': ''})
        ]
        mock_create_file.assert_has_calls(file_calls, any_order=True)

        dir_patcher.stop()
        file_patcher.stop()
        patcher.stop()

    def test_create_feature_ok(self):
        mock_result = _d.Result()
        mock_result.ok = {
            'apps': '__ABC__',
            'feature': '__123__',
            'structure': {
                'root': {
                    'files': ['fake_file'],
                    'dirs': ['dir_1', 'dir_2']
                }
            },
            'features': {
                'apps': {
                    'files': ['fake_file.py'],
                    'dirs': ['root']
                }
            }
        }
        patcher = patch(f'{self.APPS_PATH}.Config.load_config')
        mock_cfg = patcher.start()
        mock_cfg.return_value = mock_result

        result = _d.Result()
        result.ok = 'this is ok'
        sassy = _a.Sassy(apps='test_sassy', message=self.message)
        file_patcher = patch(f'{self.APPS_PATH}.Sassy.create_file')

        mock_create_file = file_patcher.start()
        mock_create_file.return_value = result

        sassy.create_feature(feature='fake_feature')

        file_calls = [
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_1/fake_file.py':
                    ''}),
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/test_sassy/dir_2/fake_file.py':
                    ''})
        ]
        mock_create_file.assert_has_calls(file_calls, any_order=True)

        file_patcher.stop()
        patcher.stop()

    @pytest.mark.parametrize('idx, show', [
        (0, 'ok'),
        (1, 'err'),
        (2, 'all'),
    ])
    def test_printer_ok(self, idx, show):
        """
        This test aims to evaluate the show attributes.
        logging.debug is patched with a mock as an Exception
        Everytime show attributes is valid we raise an Exception
        """
        patcher = patch(f'{self.APPS_PATH}._VERBOSE', 'debug')
        log_patcher = patch(f'{self.APPS_PATH}.Logger.log')
        patcher.start()
        mock = log_patcher.start()
        mock.side_effect = Exception('123')

        @_a.printer(show=show, verbose='debug')
        def foo():
            r = _d.Result()
            if show == 'err':
                r.err = 'this is an error'
            else:
                r.ok = 'this is ok'
            return r

        with pytest.raises(Exception):
            foo()

        patcher.stop()
        log_patcher.stop()

    def test_printer_show_not_ok(self):
        """
        This test aims to evaluate the show attributes.
        logging.debug is patched with a mock as an Exception
        Everytime show attributes is invalid we do not raise an Exception
        The function return the value Result
        """
        @_a.printer(show='invalid', verbose='debug')
        def foo():
            r = _d.Result()
            r.ok = 'this is ok'
            return r

        assert isinstance(foo(), _d.Result)

    def test_printer_ok_with_no_args(self):
        """
        No args provide to the decorator printer
        The function return the value Result
        """
        @_a.printer
        def foo():
            r = _d.Result()
            r.ok = 'this is ok'
            return r

        assert isinstance(foo(), _d.Result)

    # @pytest.mark.parametrize('idx, sev', [
    #     (0, 'DEBUG'),
    #     (0, 'INFO'),
    #     (0, 'WARNING'),
    #     (0, 'ERROR'),
    #     (0, 'CRITICAL'),
    # ])
    # def test_show_logging(self, idx, sev):
    #     message = _d.Message(
    #         code=100,
    #         severity=sev
    #     )
    #     message.text = 'A fake message'
    #     _a.Logger.log(message=message)
