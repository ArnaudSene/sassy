"""
Unit test for _sassy.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import os
from unittest.mock import patch, mock_open


import _sassy.d_sassy as _d
import _sassy.p_sassy as _p
import _sassy.a_sassy as _a


class TestSassy:
    """Main test for Sassy."""

    APPS_PATH = '_sassy.a_sassy'
    _a._VERBOSE = False
    cwd = os.path.dirname(os.path.abspath(__file__))
    yaml_file = "/".join([cwd, 'sassy.yml'])

    def test_sassy_load_config_ok(self):
        """load_config return a dict."""
        sassy = _a.Sassy(apps='test_sassy')
        result = sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.ok

    def test_sassy_load_config_file_not_found(self):
        """load_config raise FileNotFoundError."""
        sassy = _a.Sassy(apps='test_sassy')
        sassy.config_file = 'bad_file'
        result = sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.err

    def test_sassy_load_config_bad_format(self):
        """load_config raise ParserError."""
        sassy = _a.Sassy(apps='test_sassy')
        yaml_file = "/".join([self.cwd, 'test_sassy.py'])
        sassy.config_file = yaml_file
        result = sassy.load_config()
        assert isinstance(result, _d.Result)
        assert result.err

    def test_load_config_keyword_missing(self):
        sassy = _a.Sassy(apps='test_sassy')
        sassy.config_file = self.cwd + '/fake_sassy.yml'
        r = sassy.load_config()
        assert r.err.code == 402

    def test_define_file_file_as_str_ok(self):
        """Define the file format as a dict."""
        sassy = _a.Sassy(apps='test_sassy')
        file = 'a file'
        expected = {file: ""}
        result = sassy.define_file(file=file)
        assert result == expected

    def test_define_file_file_as_dict_ok(self):
        """Define the file format as a dict."""
        sassy = _a.Sassy(apps='test_sassy')
        file = {'a file': 'content'}
        expected = file
        result = sassy.define_file(file=file)
        assert result == expected

    def test_replace_apps_content(self):
        """Replace content with apps"""
        sassy = _a.Sassy(apps='test_sassy')
        content = '"""Some content with __APPS__."""'
        expected = content.replace('__APPS__', sassy.apps)
        new_content = sassy.replace_apps_content(content)
        assert new_content == expected

    def test_new_path(self):
        sassy = _a.Sassy(apps='test_sassy')
        path = sassy._PATH
        apps = sassy.apps
        apps_path = "/".join([path, apps])
        assert sassy.apps_path == apps_path

    def test_create_files_and_dirs_invalid_kw(self):
        sassy = _a.Sassy(apps='test_sassy')
        sassy.cfg = {sassy._STRUCTURE: {}}
        r = sassy.create_files_and_dirs(kw_main='invalid_kw')
        assert r.err.code == 202

    def test_create_files_and_dirs_create_dir_files_ok(self):
        sassy = _a.Sassy(apps='test_sassy')
        sassy.cfg = {sassy._STRUCTURE: {'good_kw': {}}}
        r = sassy.create_files_and_dirs(kw_main='good_kw')
        assert r.ok.code == 104

    def test_create_files_and_dirs_success(self):
        sassy = _a.Sassy(apps='test_sassy')
        sassy.cfg = {sassy._STRUCTURE: {'good_kw': {}}}
        message = _p.MessageService()
        self.result = message.msg(name='dir_create_ok')

        patcher = patch(f'{self.APPS_PATH}.Sassy.create_dir')
        mock_create_dir = patcher.start()
        mock_create_dir.return_value = self.result

        r = sassy.create_files_and_dirs(kw_main='good_kw')
        patcher.stop()

    def test_create_file_already_exist(self):
        sassy = _a.Sassy(apps='test_sassy')
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{self.APPS_PATH}.os.path.isfile')
        mock_isfile = patcher.start()
        mock_isfile.return_value = True
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 200
        patcher.stop()

    def test_create_file_success_with_dir_name(self):
        sassy = _a.Sassy(apps='test_sassy')
        fake_file = 'fake_file.py'
        fake_file_path = 'fake/file/path'
        content = "Message to write on file to be written"

        with patch(f'{self.APPS_PATH}.open', mock_open()) as mocked_file:
            r = sassy.create_file(
                files={fake_file: content}, dir_name=fake_file_path)

            mocked_file.assert_called_once_with(
                f"{sassy.apps_path}/{fake_file_path}/{fake_file}", 'w')

            mocked_file().write.assert_called_once_with(content + "\n")
            assert r.ok.code == 101

    def test_create_file_success_without_dir_name(self):
        sassy = _a.Sassy(apps='test_sassy')
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"

        with patch(f'{self.APPS_PATH}.open', mock_open()) as mocked_file:
            r = sassy.create_file(files={fake_file: content})

            mocked_file.assert_called_once_with(
                f"{sassy.apps_path}/{fake_file}", 'w')

            mocked_file().write.assert_called_once_with(content + "\n")
            assert r.ok.code == 101

    def test_create_file_failed_raise_exception(self):
        sassy = _a.Sassy(apps='test_sassy')
        fake_file = 'fake_file.py'
        content = "Message to write on file to be written"
        patcher = patch(f'{self.APPS_PATH}.open')
        mock_open_ = patcher.start()
        mock_open_.side_effect = Exception('fake_error')
        r = sassy.create_file(files={fake_file: content})
        assert r.err.code == 301
        patcher.stop()

    def tests_create_dir_already_exist(self):
        sassy = _a.Sassy(apps='test_sassy')
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
        sassy = _a.Sassy(apps='test_sassy')
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
        sassy = _a.Sassy(apps='test_sassy')
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

    def tests_create_dir_failed_with_oserror_exception(self):
        sassy = _a.Sassy(apps='test_sassy')
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
        sassy = _a.Sassy(apps='test_sassy')
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        name = 'fake_name'
        sassy.create_dir(name=name)
        mock_isdir.assert_called_once_with(f"{sassy.apps_path}/{name}")
        isdir_patcher.stop()

    def test_create_dir_success_without_params(self):
        sassy = _a.Sassy(apps='test_sassy')
        sassy.update = False
        isdir_patcher = patch(f'{self.APPS_PATH}.os.path.isdir')
        mock_isdir = isdir_patcher.start()
        mock_isdir.return_value = True
        sassy.create_dir()
        mock_isdir.assert_called_once_with(f"{sassy.apps_path}")
        isdir_patcher.stop()
