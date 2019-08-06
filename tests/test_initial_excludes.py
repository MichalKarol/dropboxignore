from unittest.mock import patch, MagicMock
from dropboxignore import initial_excludes, Rules


@patch('dropboxignore.test_if_ignored', lambda *_, **__: False)
@patch('os.scandir')
def test_initial_excludes_no_ignore(scandir_mock):
    # GIVEN
    dir_entry = MagicMock(path='mock_dir', is_dir=MagicMock(return_value=True))
    file_entry = MagicMock(path='mock_file', is_dir=MagicMock(return_value=False))
    scandir_mock.side_effect = [[dir_entry], [file_entry]]

    # WHEN
    initial_excludes('mock_path', Rules([], []))

    # THEN
    assert dir_entry.is_dir.called
    assert file_entry.is_dir.called


@patch('dropboxignore.test_if_ignored', lambda *_, **__: True)
@patch('dropboxignore.dropbox_exclude')
@patch('os.scandir')
def test_initial_excludes_ignored(scandir_mock, dropbox_exclude_mock):
    # GIVEN
    dir_entry = MagicMock(path='mock_dir', is_dir=MagicMock(return_value=True))
    file_entry = MagicMock(path='mock_file', is_dir=MagicMock(return_value=False))
    scandir_mock.side_effect = [[dir_entry], [file_entry]]

    # WHEN
    initial_excludes('mock_path', Rules([], []))

    # THEN
    assert dir_entry.is_dir.called
    assert not file_entry.is_dir.called
    assert dropbox_exclude_mock.called


@patch('dropboxignore.test_if_ignored', lambda *_, **__: True)
@patch('dropboxignore.dropbox_exclude')
@patch('os.scandir')
def test_initial_excludes_file_ignored(scandir_mock, dropbox_exclude_mock):
    # GIVEN
    file_entry = MagicMock(path='mock_file', is_dir=MagicMock(return_value=False))
    scandir_mock.side_effect = [[file_entry]]

    # WHEN
    initial_excludes('mock_path', Rules([], []))

    # THEN
    assert file_entry.is_dir.called
    assert not dropbox_exclude_mock.called
