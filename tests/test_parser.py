from dropboxignore import parse_dropboxignore


def test_empty_line():
    # GIVEN
    pattern = ''

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 0


def test_comment_line():
    # GIVEN
    pattern = '#123'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 0


def test_hash_starting_line(subtests):
    # GIVEN
    pattern = '\\#test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('#test')
    assert rules.ignored[0].match('test/#test')
    assert rules.ignored[0].match('some_more test/#test')
    assert rules.ignored[0].match('some_more test/#test/or\\ even more')


def test_basic_pattern():
    # GIVEN
    pattern = 'test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('tested/test')
    assert rules.ignored[0].match('some_more test/test')
    assert rules.ignored[0].match('some_more test/test/or\\ even more')


def test_star_pattern():
    # GIVEN
    pattern = '*test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('aatest/more')
    assert rules.ignored[0].match('some_more dir/aatest')
    assert rules.ignored[0].match('some_more dir/bbtest/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/bbtestcc/or\\ even more')


def test_star_pattern_both_side():
    # GIVEN
    pattern = '*test*'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('aatest/more')
    assert rules.ignored[0].match('some_more dir/aatest')
    assert rules.ignored[0].match('some_more dir/bbtest/or\\ even more')
    assert rules.ignored[0].match('some_more dir/bbtestcc/or\\ even more')


def test_star_pattern_inside():
    # GIVEN
    pattern = 'te*st'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('teaast/more')
    assert rules.ignored[0].match('some_more dir/teaast')
    assert rules.ignored[0].match('some_more dir/tebbst/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/teccstss/or\\ even more')


def test_qmark_pattern():
    # GIVEN
    pattern = '?test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert not rules.ignored[0].match('test')
    assert rules.ignored[0].match('atest/more')
    assert not rules.ignored[0].match('aatest/more')
    assert rules.ignored[0].match('some_more dir/atest')
    assert not rules.ignored[0].match('some_more dir/aatest')
    assert rules.ignored[0].match('some_more dir/btest/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/btestc/or\\ even more')


def test_qmark_pattern_both_side():
    # GIVEN
    pattern = '?test?'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert not rules.ignored[0].match('test')
    assert rules.ignored[0].match('atesta/more')
    assert not rules.ignored[0].match('aatesta/more')
    assert rules.ignored[0].match('some_more dir/atesta')
    assert not rules.ignored[0].match('some_more dir/aatesta')
    assert rules.ignored[0].match('some_more dir/btestb/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/bbtestc/or\\ even more')


def test_qmark_pattern_inside():
    # GIVEN
    pattern = 'te?st'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert not rules.ignored[0].match('test')
    assert rules.ignored[0].match('teast/more')
    assert not rules.ignored[0].match('teaast/more')
    assert rules.ignored[0].match('some_more dir/teast')
    assert not rules.ignored[0].match('some_more dir/teaast')
    assert rules.ignored[0].match('some_more dir/tebst/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/tebbcst/or\\ even more')


def test_double_star_pattern_begin():
    # GIVEN
    pattern = '**/test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('test/more')
    assert not rules.ignored[0].match('atest/more')
    assert rules.ignored[0].match('some_more dir/test')
    assert not rules.ignored[0].match('some_more dir/atest')
    assert rules.ignored[0].match('some_more dir/test/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/testa/or\\ even more')


def test_double_star_pattern_end():
    # GIVEN
    pattern = 'test/**'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert rules.ignored[0].match('test/more')
    assert not rules.ignored[0].match('testa/more')
    assert rules.ignored[0].match('some_more dir/test')
    assert not rules.ignored[0].match('some_more dir/testa')
    assert rules.ignored[0].match('some_more dir/test/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/atesta/or\\ even more')


def test_double_star_pattern_inside():
    # GIVEN
    pattern = 'a/**/test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert not rules.ignored[0].match('test')
    assert not rules.ignored[0].match('test/more')
    assert rules.ignored[0].match('a/test/more')
    assert not rules.ignored[0].match('a/testa/more')
    assert not rules.ignored[0].match('some_more dir/test')
    assert not rules.ignored[0].match('some_more dir/testa')
    assert rules.ignored[0].match('a/some_more dir/test')
    assert not rules.ignored[0].match('some_more dir/test/or\\ even more')
    assert not rules.ignored[0].match('some_more dir/atesta/or\\ even more')
    assert rules.ignored[0].match('a/some/some_more dir/test/or\\ even more')


def test_whatespaces():
    # GIVEN
    pattern = 'test\\ and\\ whitespace'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test and whitespace')
    assert rules.ignored[0].match('aaa/test and whitespace')
    assert rules.ignored[0].match('aaa/test and whitespace/more')


def test_ranges():
    # GIVEN
    pattern = 'test[0-9]'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test1')
    assert rules.ignored[0].match('aaa/test2')
    assert rules.ignored[0].match('aaa/test0/more')
    assert not rules.ignored[0].match('aaa/test00/more')
    assert not rules.ignored[0].match('aaa/testa/more')


def test_set():
    # GIVEN
    pattern = 'test[09]'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test0')
    assert rules.ignored[0].match('aaa/test9')
    assert rules.ignored[0].match('aaa/test0/more')
    assert not rules.ignored[0].match('aaa/test1/more')
    assert not rules.ignored[0].match('aaa/test5/more')


def test_not_set():
    # GIVEN
    pattern = 'test[!09]'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test1')
    assert not rules.ignored[0].match('test0')
    assert not rules.ignored[0].match('test9')


def test_not_set_with_set():
    # GIVEN
    pattern = 'test[!09][09]'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test10')
    assert not rules.ignored[0].match('test01')
    assert not rules.ignored[0].match('test91')


def test_starting_with_exclamation():
    # GIVEN
    pattern = '\\!test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('!test')
    assert rules.ignored[0].match('a/!test')
    assert rules.ignored[0].match('a/!test/more')


def test_starting_with_slash():
    # GIVEN
    pattern = '/test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.ignored) == 1
    assert rules.ignored[0].match('test')
    assert not rules.ignored[0].match('a/test')
    assert not rules.ignored[0].match('a/test/more')


def test_exclude_basic():
    # GIVEN
    pattern = '!test'

    # WHEN
    rules = parse_dropboxignore([pattern])

    # THEN
    assert len(rules.excluded) == 1
    assert rules.excluded[0].match('test')
    assert rules.excluded[0].match('a/test')
    assert rules.excluded[0].match('a/test/more')

# Tests for:
# directory node_modules_old przy ignorowanym node_modules*/