from unittest.mock import patch, MagicMock
from dropboxignore import EventHandler, Rules


@patch('dropboxignore.test_if_ignored', lambda *_, **__: True)
def test_event_handler_positive():
    # GIVEN
    ignore_tree_mock = MagicMock()
    ignore_tree_mock.add_ignored.side_effect = None

    # WHEN
    ev = EventHandler('', Rules([], []), ignore_tree_mock)
    ev.process_default(MagicMock(pathname=''))

    # THEN
    ignore_tree_mock.add_ignored.assert_called_once()


@patch('dropboxignore.test_if_ignored', lambda *_, **__: False)
def test_event_handler_negative():
    # GIVEN
    ignore_tree_mock = MagicMock()
    ignore_tree_mock.add_ignored.side_effect = None

    # WHEN
    ev = EventHandler('', Rules([], []), ignore_tree_mock)
    ev.process_default(MagicMock(pathname=''))

    # THEN
    assert not ignore_tree_mock.called
