from unittest.mock import patch, MagicMock
from dropboxignore import EventHandler, Rules


@patch('dropboxignore.test_if_ignored', lambda *_, **__: True)
@patch('dropboxignore.dropbox_exclude')
def test_event_handler_positive(dropbox_exclude_mock):
    # GIVEN

    # WHEN
    ev = EventHandler('', Rules([], []))
    ev.process_default(MagicMock(pathname=''))

    # THEN
    dropbox_exclude_mock.assert_called_once()


@patch('dropboxignore.test_if_ignored', lambda *_, **__: False)
@patch('dropboxignore.dropbox_exclude')
def test_event_handler_negative(dropbox_exclude_mock):
    # GIVEN

    # WHEN
    ev = EventHandler('', Rules([], []))
    ev.process_default(MagicMock(pathname=''))

    # THEN
    assert not dropbox_exclude_mock.called
