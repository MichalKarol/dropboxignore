from mock import MagicMock, patch

from dropboxignore import build_initial_tree, Rules


@patch('os.path.relpath', lambda *_, **__: 'a')
@patch('os.path.normpath', lambda *_, **__: 'a')
@patch('os.scandir')
def test_build_initial_tree_iteration(scandir_mock):
    # GIVEN
    scandir_mock.side_effect = [
        [
            MagicMock(is_dir=lambda *_: True, path='a'),
            MagicMock(is_dir=lambda *_: True, path='b')
        ],
        [],
        [],
    ]

    # WHEN
    build_initial_tree('', Rules([], []))

    # THEN
    assert scandir_mock.call_count == 3


@patch('os.path.relpath', lambda *_, **__: 'a')
@patch('os.path.normpath', lambda *_, **__: 'a')
@patch('dropboxignore.test_if_ignored')
@patch('dropboxignore.IgnoreTree')
@patch('os.scandir')
def test_build_initial_tree_ignore_stops_iteration(scandir_mock, ignore_tree_mock, test_if_ignored_mock):
    # GIVEN
    test_if_ignored_mock.side_effect = [True, False, False, False]
    ignore_tree_mock().add_ignored.return_value = None
    scandir_mock.side_effect = [
        [
            MagicMock(is_dir=lambda *_: True, path='a'),
            MagicMock(is_dir=lambda *_: True, path='b'),
        ],
        [
            MagicMock(is_dir=lambda *_: True, path='c'),
        ],
        [
            MagicMock(is_dir=lambda *_: True, path='d'),
        ],
        [],
    ]

    # WHEN
    build_initial_tree('', Rules([], []))

    # THEN
    assert scandir_mock.call_count == 4
    ignore_tree_mock().add_ignored.assert_called_once_with('a')


@patch('os.path.relpath', lambda *_, **__: 'a')
@patch('os.path.normpath', lambda *_, **__: 'a')
@patch('os.scandir')
def test_build_initial_tree_skip_not_dirs(scandir_mock):
    # GIVEN
    scandir_mock.side_effect = [
        [
            MagicMock(is_dir=lambda *_: False, path='a'),
        ],
        [
            MagicMock(is_dir=lambda *_: True, path='c'),
        ],
        [],
    ]

    # WHEN
    build_initial_tree('', Rules([], []))

    # THEN
    assert scandir_mock.call_count == 1
