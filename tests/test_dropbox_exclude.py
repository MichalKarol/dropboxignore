from unittest.mock import patch, MagicMock
from dropboxignore import dropbox_exclude


@patch('subprocess.check_output')
@patch('subprocess.call')
def test_dropbox_exclude_no_already_excluded(call_mock, check_output_mock):
    # GIVEN
    check_output_mock.return_value = b'Excluded:\n'

    # WHEN
    dropbox_exclude('', '')

    # THEN
    assert call_mock.called


@patch('subprocess.check_output')
@patch('subprocess.call')
def test_dropbox_exclude_already_excluded_exact(call_mock, check_output_mock):
    # GIVEN
    check_output_mock.return_value = b'Excluded:\npath\n'

    # WHEN
    dropbox_exclude('path', '')

    # THEN
    assert not call_mock.called


@patch('subprocess.check_output')
@patch('os.path.sep', '/')
@patch('subprocess.call')
def test_dropbox_exclude_already_excluded_subpath(call_mock, check_output_mock):
    # GIVEN
    check_output_mock.return_value = b'Excluded:\npath\n'

    # WHEN
    dropbox_exclude('path/subpath', '')

    # THEN
    assert not call_mock.called
