"""
Unit test for _sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import os
import typing as _t
from unittest.mock import patch, mock_open, call

import git
import pytest

from _sassy.a_sassy import InitRepo, Config, Sassy, MessageLogger
from _sassy.d_sassy import Message, File, Result
from _sassy.i_sassy import RepoInterface
from _sassy.p_sassy import MessageService, RepoProvider, Logger


class FakeRepoProvider(RepoInterface):
    """``RepoProvider`` class."""

    COMMIT = 'c15bb53be41105da0b3163e485c534a314085e89'
    RAISE = None

    def result(self):
        if self.RAISE:
            raise self.RAISE
        return self.COMMIT

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
            return self.result()

        except Exception:
            raise


APPS_PATH = '_sassy.a_sassy'
PROVIDER_PATH = '_sassy.p_sassy'


@patch(f"{APPS_PATH}.logger_provider.verbose", False)
class TestSassy:
    """Main test for Sassy."""

    repo = FakeRepoProvider()

    _VERBOSE = False
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = "/".join(tests_dir.split('/')[:-1])
    sassy_dir = "/".join([cwd, '_sassy'])
    yaml_file = "/".join([sassy_dir, 'sassy.yml'])
    message = MessageService()
    yaml_load = {
        'apps': '__ABC__',
        'feature': '__123__',
        'structure': {
            'apps': {
                'files': ['fake_file'],
                'dirs': ['apps_dir_1', 'apps_dir_2']
            },
            'other': {
                'files': ['fake_file'],
                'dirs': ['other_dir_1', 'other_dir_2']
            },
            'tests': {
                'dirs': ['tests/tests_dir_1', 'tests/tests_dir_2']
            },
        },
        'features': {
            'apps': {
                'files': ['__123__.py'],
                'dirs': ['apps']
            },
            'tests': {
                'files': ['test___123__.py'],
                'dirs': ['tests']
            }
        }
    }

    # Domains

    def test_result_dto_ok_or_err(self):
        """ok or err but not both together."""
        r = Result()
        r.err = 'err'
        r.ok = 'ok'
        assert r.ok
        assert not r.err

    def test_result_dto_as_str_ok(self):
        """rewrite __str__."""
        r = Result()
        r.ok = 'this is a string'

        assert str(r) == 'this is a string'

    def test_result_dto_as_str_err(self):
        """rewrite __str__."""
        r = Result()
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
        m = Message(code, severity, extra)
        assert m.level() == lvl

    def test_message_dto_reps(self):
        """rewrite __repr__."""
        code = 999
        severity = 'TEST'
        extra = 'extra'
        text = 'a fake text'
        expected = f"Message(code: {code}, severity: {severity}, text: {text})"

        m = Message(code, severity, extra)
        m.text = text

        assert repr(m) == expected

    def test_message_dto_as_str(self):
        """rewrite __str__."""
        code = 999
        severity = 'TEST'
        extra = 'extra'
        text = 'a fake text'
        expected = f"({code},{severity},{text})"

        m = Message(code, severity, extra)
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

        m = Message(code, severity, extra)
        m.text = text

        assert m.as_dict() == expected

    # Applications

    def test_message_logger_ok(self):
        """call logger.show with result.ok"""
        logger = Logger(verbose=False)
        message = Message(code=999, severity='INFO')
        message.text = 'abc'
        result = Result()
        result.ok = message

        @MessageLogger(logger=logger, show='all')
        def foo(r):
            return r

        with patch('_sassy.p_sassy.Logger.show') as mock:
            rr = foo(result)
            mock.assert_called_with(message=result.ok)
            assert rr == result

    def test_message_logger_err(self):
        """call logger.show with result.err"""
        logger = Logger(verbose=False)
        message = Message(code=999, severity='INFO')
        message.text = 'abc'
        result = Result()
        result.err = message

        @MessageLogger(logger=logger, show='all')
        def foo(r):
            return r

        with patch('_sassy.p_sassy.Logger.show') as mock:
            rr = foo(result)
            mock.assert_called_with(message=result.err)
            assert rr == result

    def test_message_logger_show_invalid(self):
        """no call logger.show because show=abc is invalid"""
        logger = Logger(verbose=False)
        message = Message(code=999, severity='INFO')
        message.text = 'abc'
        result = Result()
        result.err = message

        @MessageLogger(logger=logger, show='abc')
        def foo(r):
            return r

        with patch('_sassy.p_sassy.Logger.show') as mock:
            rr = foo(result)
            mock.assert_not_called()
            assert rr == result

    def test_message_logger_no_result(self):
        """return func, not a Result instance"""
        logger = Logger(verbose=False)
        result = 'abc'

        @MessageLogger(logger=logger, show='all')
        def foo(r):
            return r

        with patch('_sassy.p_sassy.Logger.show') as mock:
            rr = foo(result)
            mock.assert_not_called()
            assert rr == result

    def test_sassy_load_config_ok(self):
        """load_config return a dict."""
        config = Config(message=self.message)
        result_cfg = config.load_config(config_file=self.yaml_file)
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        assert result_cfg.ok == sassy.cfg

    def test_sassy_load_config_bad_format(self):
        """load_config raise ParserError."""
        config = Config(message=self.message)
        yaml_file = "/".join([self.tests_dir, 'test_sassy.py'])
        result = config.load_config(config_file=yaml_file)
        assert result.err.code == 400

    def test_sassy_load_config_file_not_found(self):
        """load_config raise FileNotFoundError."""
        config_file = 'bad_file'
        config = Config(message=self.message)
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
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        file: File = sassy._get_file_dto(files=files)
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
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        file: File = sassy._get_file_dto(files=files)
        assert file is None

    def test__get_struct_dto_not_ok(self):
        """Invalid yaml file or missing keyword. Result is []"""
        yaml_load = {'kw': 'invalid'}
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = yaml_load
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        result = sassy._get_struct_dto()
        assert not result
        patcher.stop()

    def test__get_struct_dto_ok(self):
        """Valid yaml file. Result is list of Struct DTO"""
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = self.yaml_load

        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        result = sassy._get_struct_dto()
        assert result[0].name == 'apps'
        assert result[0].dirs == ['apps_dir_1', 'apps_dir_2']
        assert result[0].files == [File(name='fake_file')]
        patcher.stop()

    def test__get_feature_structure_dto_not_ok(self):
        """Invalid yaml file or missing keyword. Result is []"""
        yaml_load = {'kw': 'invalid'}
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = yaml_load
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        result = sassy._get_feature_structure_dto()
        assert not result
        patcher.stop()

    def test__get_feature_structure_dto_ok(self):
        """Valid yaml file. Result is list of Struct DTO"""
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = self.yaml_load
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        result = sassy._get_feature_structure_dto()
        assert result[0].name == 'apps'
        assert result[0].dirs == ['apps_dir_1', 'apps_dir_2']
        assert result[0].files == [File(name='__123__.py', content='')]
        patcher.stop()

    def tests_create_dir_already_exist(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.err.code == 201

    def tests_create_dir_success(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = False
        makedir_patcher = patch(f'{APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.ok.code == 102

    def tests_create_dir_success_already_exist(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = True
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{APPS_PATH}.os.makedirs')
        makedir_patcher.start()

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.ok.code == 102

    def tests_create_dir_failed_with_os_error_exception(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = True
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        makedir_patcher = patch(f'{APPS_PATH}.os.makedirs')
        mock_makedir = makedir_patcher.start()
        mock_makedir.side_effect = OSError

        r = sassy.create_dir(name='fake_name')
        isdir_patcher.stop()
        makedir_patcher.stop()
        assert r.err.code == 302

    def test_create_dir_success_with_params(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        name = 'fake_name'
        sassy.create_dir(name=name)
        mock_isdir.assert_called_once_with(name)
        isdir_patcher.stop()

    def test_create_dir_success_without_params(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isdir_patcher = patch(f'{APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        sassy.create_dir()
        mock_isdir.assert_called_once_with(f"{sassy.apps_path}")
        isdir_patcher.stop()

    def test_create_file_already_exist(self):
        """File is already exist"""
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{APPS_PATH}.os.path.isfile')
        mock_isfile = patcher.start()
        mock_isfile.return_value = True
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 200
        patcher.stop()

    def test_create_file_success_ok(self):
        """Write file ok"""
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        fake_file = 'fake/file/path/fake_file.py'
        content = "Message to write on file to be written"

        with patch(f'{APPS_PATH}.open', mock_open()) as mocked_file:
            r = sassy.create_file(files={fake_file: content})

            mocked_file.assert_called_once_with(f"{fake_file}", 'w')

            mocked_file().write.assert_called_once_with(content + "\n")
            assert r.ok.code == 101

    def test_create_file_failed_raise_exception(self):
        """Raise exception"""
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{APPS_PATH}.open')
        mock_open_ = patcher.start()
        mock_open_.side_effect = Exception('fake_error')
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 301
        patcher.stop()

    def tests_delete_file_success(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isfile_patcher = patch(f'{APPS_PATH}.os.path.isfile')
        mock_isfile = isfile_patcher.start()
        mock_isfile.return_value = True

        os_remove_patcher = patch(f'{APPS_PATH}.os.remove')
        os_remove_patcher.start()

        r = sassy.delete_file(file='fake_file_name')
        isfile_patcher.stop()
        os_remove_patcher.stop()
        assert r.ok.code == 106

    def tests_delete_file_raise_exception(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isfile_patcher = patch(f'{APPS_PATH}.os.path.isfile')
        mock_isfile = isfile_patcher.start()
        mock_isfile.return_value = True

        os_remove_patcher = patch(f'{APPS_PATH}.os.remove')
        mock_remove = os_remove_patcher.start()
        mock_remove.side_effect = Exception('fake error')

        r = sassy.delete_file(file='fake_file_name')
        isfile_patcher.stop()
        os_remove_patcher.stop()
        assert r.err.code == 303

    def tests_delete_file_file_not_exist(self):
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        sassy.update = False
        isfile_patcher = patch(f'{APPS_PATH}.os.path.isfile')
        mock_isfile = isfile_patcher.start()
        mock_isfile.return_value = False

        r = sassy.delete_file(file='fake_file_name')
        assert r.err.code == 203

        isfile_patcher.stop()

    def test_replace_content_ok(self):
        """replace ok"""
        content = '"""this is a test for __APPS__."""'
        expected = '"""this is a test for replaced_value."""'
        file = File(name='fake', content=content)
        payload = {
            '__APPS__': 'replaced_value',
            'inexist': 'nothing'
        }
        assert file.replace_content(payload) == expected

    def test_replace_content_not_ok(self):
        """Nothing replaced"""
        content = '"""this is a test for __APPS__."""'
        expected = '"""this is a test for __APPS__."""'
        file = File(name='fake', content=content)
        payload = {
            'inexist': 'nothing'
        }
        assert file.replace_content(payload) == expected

    def test_create_structure_ok(self):
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = self.yaml_load

        result = Result()
        result.ok = 'this is ok'
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)

        dir_patcher = patch(f'{APPS_PATH}.Sassy.create_dir')
        file_patcher = patch(f'{APPS_PATH}.Sassy.create_file')
        mock_create_dir = dir_patcher.start()
        mock_create_dir.return_value = result
        mock_create_file = file_patcher.start()
        mock_create_file.return_value = result

        sassy.create_structure()
        dir_calls = [
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'fake_sassy/apps_dir_1'),
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'fake_sassy/apps_dir_2'),
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'fake_sassy/other_dir_1'),
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'fake_sassy/other_dir_2'),
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'tests/tests_dir_1'),
            call(name='/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                      'tests/tests_dir_2'),
        ]
        mock_create_dir.assert_has_calls(dir_calls, any_order=True)

        file_calls = [
            call(files={'/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                        'fake_sassy/apps_dir_1/fake_file': ''}),
            call(files={'/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                        'fake_sassy/apps_dir_2/fake_file': ''}),
            call(files={'/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                        'fake_sassy/other_dir_1/fake_file': ''}),
            call(files={'/Volumes/SSD_Data/halia/Sassy/fake_sassy/'
                        'fake_sassy/other_dir_2/fake_file': ''})
        ]
        mock_create_file.assert_has_calls(file_calls, any_order=True)

        dir_patcher.stop()
        file_patcher.stop()
        patcher.stop()

    def test_create_feature_ok(self):
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = self.yaml_load

        result = Result()
        result.ok = 'this is ok'
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        file_patcher = patch(f'{APPS_PATH}.Sassy.create_file')

        mock_create_file = file_patcher.start()
        mock_create_file.return_value = result
        sassy.create_feature(feature='fake_feature')

        file_calls = [
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/fake_sassy/fake_sassy'
                '/apps_dir_1/fake_feature.py': ''}),
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/fake_sassy/fake_sassy'
                '/apps_dir_2/fake_feature.py': ''}),
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/fake_sassy/tests'
                '/tests_dir_1/test_fake_feature.py': ''}),
            call(files={
                '/Volumes/SSD_Data/halia/Sassy/fake_sassy/tests'
                '/tests_dir_2/test_fake_feature.py': ''})
        ]

        mock_create_file.assert_has_calls(file_calls, any_order=True)

        file_patcher.stop()
        patcher.stop()

    def test_delete_feature_ok(self):
        patcher = patch(f'{APPS_PATH}._yaml.load')
        mock_cfg = patcher.start()
        mock_cfg.return_value = self.yaml_load
        result = Result()
        result.ok = 'this is ok'
        sassy = Sassy(
            apps='fake_sassy', message=self.message, repo=self.repo)
        file_patcher = patch(f'{APPS_PATH}.Sassy.delete_file')
        mock_delete_file = file_patcher.start()
        mock_delete_file.return_value = result
        sassy.delete_feature(feature='fake_feature')

        file_calls = [
            call(file='/Volumes/SSD_Data/halia/Sassy/fake_sassy/fake_sassy'
                      '/apps_dir_1/fake_feature.py'),
            call(file='/Volumes/SSD_Data/halia/Sassy/fake_sassy/fake_sassy'
                      '/apps_dir_2/fake_feature.py'),
            call(file='/Volumes/SSD_Data/halia/Sassy/fake_sassy/tests'
                      '/tests_dir_1/test_fake_feature.py'),
            call(file='/Volumes/SSD_Data/halia/Sassy/fake_sassy/tests'
                      '/tests_dir_2/test_fake_feature.py')]

        mock_delete_file.assert_has_calls(file_calls, any_order=True)

        file_patcher.stop()
        patcher.stop()

    def test_init_repo_ok(self):
        """Init repo and return a commit number."""
        repo_name = 'fake_repo_name'
        items = ['dirs_1', 'files_a']
        repo = FakeRepoProvider()
        result = InitRepo(repo=repo, message=self.message)(
            repo_name=repo_name,
            items=items,
        )
        assert result.ok.code == 107

    def test_init_repo_not_ok(self):
        """Init repo and raise exception."""
        repo_name = 'fake_repo_name'
        items = ['dirs_1', 'files_a']
        repo = FakeRepoProvider()
        repo.RAISE = Exception('fake error')
        result = InitRepo(repo=repo, message=self.message)(
            repo_name=repo_name,
            items=items,
        )
        assert result.err.code == 304

    # Provider

    def test_repo_provider_init(self):
        """"""
        expected = '123123123123123123'

        repo_name = 'fake_repo_name'
        items = ['dirs_1', 'files_a']
        patcher = patch(f'{PROVIDER_PATH}.RepoProvider._git_init')
        patcher_add = patch(f'{PROVIDER_PATH}.RepoProvider._git_add')
        patcher_commit = patch(f'{PROVIDER_PATH}.RepoProvider._git_commit')
        patcher.start()
        patcher_add.start()
        mock_git = patcher_commit.start()
        mock_git.return_value = expected
        repo = RepoProvider()
        r = repo.init(repo_name=repo_name, items=items)
        assert r == expected
        patcher.stop()
        patcher_add.stop()
        patcher_commit.stop()

    def test_message_provider(self):
        m = MessageService()
        result = m.msg(name='invalid')
        assert result.code == 300

    def test_logger_show_log_debug(self):
        logger = Logger(verbose=True)
        message = Message(code=999, severity='DEBUG')
        with patch('_sassy.p_sassy.logging.Logger.debug') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_info(self):
        logger = Logger(verbose=True)
        message = Message(code=999, severity='INFO')
        with patch('_sassy.p_sassy.logging.Logger.info') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_warning(self):
        logger = Logger(verbose=True)
        message = Message(code=999, severity='WARNING')
        with patch('_sassy.p_sassy.logging.Logger.warning') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_error(self):
        logger = Logger(verbose=True)
        message = Message(code=999, severity='ERROR')
        with patch('_sassy.p_sassy.logging.Logger.error') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_critical(self):
        logger = Logger(verbose=True)
        message = Message(code=999, severity='CRITICAL')
        with patch('_sassy.p_sassy.logging.Logger.critical') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_other(self):
        """invalid severity, log.info is used"""
        logger = Logger(verbose=True)
        message = Message(code=999, severity='OTHER')
        with patch('_sassy.p_sassy.logging.Logger.info') as mock:
            logger.show(message=message)
            mock.assert_called()

    def test_logger_show_log_verbose_false_no_call(self):
        """verbose false no call to any log"""
        logger = Logger(verbose=False)
        message = Message(code=999, severity='INFO')
        with patch('_sassy.p_sassy.logging.Logger.info') as mock:
            logger.show(message=message)
            mock.assert_not_called()

    def test_repo_provider_git_add(self):
        repo_provider = RepoProvider()
        repo = git.Repo
        items = ['abc', 'def']

        expected = [
            (100644, 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 0, 'abc'),
            (100644, 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 0, 'def')]

        with patch('_sassy.p_sassy.RepoProvider._git_add') as mock:
            mock.return_value = expected
            result = repo_provider._git_add(
                repo=repo,
                items=items
            )
            assert result == expected
