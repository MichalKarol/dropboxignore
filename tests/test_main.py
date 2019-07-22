from mock import patch, mock_open
from pyinotify import NotifierError
import pytest


from dropboxignore import main, RETURN_CODES, ParsingException


@patch('sys.argv', ['path'])
@patch('dropboxignore.main')
def test_main_with_wrong_number_of_arguments(main_mock):
    # GIVEN

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.WRONG_NUMBER_OF_ARGS


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: False)
@patch('dropboxignore.main')
def test_main_path_not_directory(main_mock):
    # GIVEN

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.PATH_IS_NOT_DIRECTORY


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: True)
@patch('os.path.exists', lambda *_, **__: False)
@patch('dropboxignore.main')
def test_main_dropboxignore_does_not_exists(main_mock):
    # GIVEN

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.DROPBOXIGNORE_DOES_NOT_EXISTS


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: True)
@patch('os.path.exists', lambda *_, **__: True)
@patch("builtins.open")
@patch('dropboxignore.main')
def test_main_cannot_open_dropboxignore(main_mock, open_mock):
    # GIVEN
    open_mock.side_effect = Exception()

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.CANNOT_READ_DROPBOXIGNORE


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: True)
@patch('os.path.exists', lambda *_, **__: True)
@patch("builtins.open", mock_open(read_data=''))
@patch('dropboxignore.parse_dropboxignore')
@patch('dropboxignore.main')
def test_main_parse_error(main_mock, parse_dropboxignore_mock):
    # GIVEN
    parse_dropboxignore_mock.side_effect = ParsingException()

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.PARSING_ERROR


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: True)
@patch('os.path.exists', lambda *_, **__: True)
@patch("builtins.open", mock_open(read_data=''))
@patch('dropboxignore.parse_dropboxignore', lambda *_, **__: None)
@patch('dropboxignore.build_initial_tree')
@patch('dropboxignore.main')
def test_main_scanning_directory_error(main_mock, build_initial_tree_mock):
    # GIVEN
    build_initial_tree_mock.side_effect = Exception()

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.SCANNING_ERROR


@patch('sys.argv', ['path', 'otherpath'])
@patch('os.path.isdir', lambda *_, **__: True)
@patch('os.path.exists', lambda *_, **__: True)
@patch("builtins.open", mock_open(read_data=''))
@patch('dropboxignore.parse_dropboxignore', lambda *_, **__: None)
@patch('dropboxignore.build_initial_tree', lambda *_, **__: None)
@patch('pyinotify.Notifier')
@patch('dropboxignore.main')
def test_main_watch_error(main_mock, notifier_mock):
    # GIVEN
    notifier_mock().loop.side_effect = NotifierError('')

    # WHEN
    with pytest.raises(SystemExit) as exit_exception:
        main()

    # THEN
    assert exit_exception.value.code == RETURN_CODES.CANNOT_WATCH_PATH
