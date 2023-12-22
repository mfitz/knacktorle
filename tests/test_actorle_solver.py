import actorle_solver

import pytest


@pytest.mark.parametrize("movie_title_pattern, expected_regex",
                         [
                             (
                                "xxxxxx",
                                "\\w{6}$"
                             ),
                             (
                                "xxx xx xxx",
                                "\\w{3} \\w{2} \\w{3}$"
                             ),
                             (
                                "x xxxx xxxxx xx xxx",
                                "\\w{1} \\w{4} \\w{5} \\w{2} \\w{3}$"
                             ),
                         ])
def test_makes_movie_title_regex_for_title_without_special_characters(movie_title_pattern, expected_regex):
    assert actorle_solver.make_movie_title_regex(movie_title_pattern) == expected_regex


@pytest.mark.parametrize("movie_title_pattern, expected_regex",
                         [
                             (
                                "xxxxx!",
                                "\\w{5}\\!$"
                             ),
                             (
                                 "xxxxxx-xxx: xx xxx xxxx",
                                 "\\w{6}\\-\\w{3}\\: \\w{2} \\w{3} \\w{4}$"
                             ),
                             (
                                "xxxxxx'x xxxx",
                                "\\w{6}\\'\\w{1} \\w{4}$"
                             ),
                             (
                                "xxx & xx",
                                "\\w{3} \\& \\w{2}$"
                             ),
                             (
                                 "xxxxxxx xxxxxx x: xxxxxx xx xxx xxxxxxxxxx",
                                 "\\w{7} \\w{6} \\w{1}\: \\w{6} \\w{2} \\w{3} \\w{10}$"
                             )
                         ])
def test_makes_movie_title_regex_for_title_with_special_characters(movie_title_pattern, expected_regex):
    assert actorle_solver.make_movie_title_regex(movie_title_pattern) == expected_regex
