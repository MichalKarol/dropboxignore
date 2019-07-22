import re
import dropboxignore
from dropboxignore import Rules


def test_test_if_ignored_positive():
    # GIVEN
    path = 'test'
    rule = re.compile('test')

    # WHEN
    result = dropboxignore.test_if_ignored(path, Rules(ignored=[rule], excluded=[]))

    # THEN
    assert result


def test_test_if_ignored_negative():
    # GIVEN
    path = 'test'
    rule = re.compile('abcd')

    # WHEN
    result = dropboxignore.test_if_ignored(path, Rules(ignored=[rule], excluded=[]))

    # THEN
    assert not result


def test_test_if_ignored_excluded():
    # GIVEN
    path = 'atest'
    rule = re.compile('.*test')
    rule_excluded = re.compile('atest')

    # WHEN
    result = dropboxignore.test_if_ignored(path, Rules(ignored=[rule], excluded=[rule_excluded]))

    # THEN
    assert not result
