import actorle_solver

import pytest


@pytest.mark.parametrize("movie_title_pattern, expected_regex",
                         [
                             (
                                "xxxxxx",
                                "[a-zA-Z0-9]{6}$"
                             ),
                             (
                                "xxx xx xxx",
                                "[a-zA-Z0-9]{3} [a-zA-Z0-9]{2} [a-zA-Z0-9]{3}$"
                             ),
                             (
                                "x xxxx xxxxx xx xxx",
                                "[a-zA-Z0-9]{1} [a-zA-Z0-9]{4} [a-zA-Z0-9]{5} [a-zA-Z0-9]{2} [a-zA-Z0-9]{3}$"
                             ),
                         ])
def test_makes_movie_title_regex_for_title_without_special_characters(movie_title_pattern, expected_regex):
    assert actorle_solver.make_movie_title_regex(movie_title_pattern) == expected_regex


@pytest.mark.parametrize("movie_title_pattern, expected_regex",
                         [
                             (
                                "xxxxx!",
                                "[a-zA-Z0-9]{5}\\!$"
                             ),
                             (
                                 "xxxxxx-xxx: xx xxx xxxx",
                                 "[a-zA-Z0-9]{6}\\-[a-zA-Z0-9]{3}\\: [a-zA-Z0-9]{2} [a-zA-Z0-9]{3} [a-zA-Z0-9]{4}$"
                             ),
                             (
                                "xxxxxx'x xxxx",
                                "[a-zA-Z0-9]{6}\\'[a-zA-Z0-9]{1} [a-zA-Z0-9]{4}$"
                             )
                         ])
def test_makes_movie_title_regex_for_title_with_special_characters(movie_title_pattern, expected_regex):
    assert actorle_solver.make_movie_title_regex(movie_title_pattern) == expected_regex
