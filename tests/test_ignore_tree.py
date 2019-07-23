from unittest.mock import patch, MagicMock, PropertyMock

from dropboxignore import IgnoreTree


@patch('os.path.sep', '/')
def test_add_ignored_non_existing():
    # GIVEN
    path = 'a/b'

    # WHEN
    it = IgnoreTree('')
    it.add_ignored(path)

    # THEN
    assert it.tree['a']['b'].ignored


@patch('os.path.sep', '/')
def test_add_ignored_existing_parent():
    # GIVEN
    parent = 'a'
    path = 'a/b'

    # WHEN
    it = IgnoreTree('')
    it.add_ignored(parent)
    it.add_ignored(path)

    # THEN
    assert 'b' not in it.tree['a']


@patch('os.path.sep', '/')
def test_add_ignored_existing_path():
    # GIVEN
    path = 'a/b'
    it = IgnoreTree('')
    it.add_ignored(path)
    node_mock = MagicMock()
    prop_mock = PropertyMock(return_value=True)
    type(node_mock).ignored = prop_mock
    it.tree['a']['b'] = node_mock

    # WHEN
    it.add_ignored(path)

    # THEN
    prop_mock.assert_called_once()
