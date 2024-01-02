import os

import pytest

import movie_clues
from movie_clues import MovieClue


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
def test_makes_regex_for_movie_title_without_special_characters(movie_title_pattern, expected_regex):
    assert movie_clues.make_movie_title_regex(movie_title_pattern) == expected_regex


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
def test_makes_regex_for_movie_title_with_special_characters(movie_title_pattern, expected_regex):
    assert movie_clues.make_movie_title_regex(movie_title_pattern) == expected_regex


def test_round_trip_serialisation_preserves_clues_list(tmpdir):
    clues_file_path = "{}/{}".format(tmpdir, 'clues-file.txt')
    assert not os.path.exists(clues_file_path)
    clues_list = [
        MovieClue('xxxxx xxxx xxxxxxx',
                  '1996',
                  'Action,Family,Comedy',
                  2.6),
        MovieClue('xxx xxxx xx',
                  '2001',
                  'Comedy,Romance',
                  5.7),
        MovieClue('xxxxxxxxxx xxxxx xxxxxxxx',
                  '2008',
                  'Comedy,Romance,Drama',
                  7.1)
    ]

    movie_clues.write_movie_clues_file(clues_file_path, clues_list)
    assert os.path.exists(clues_file_path)
    assert os.path.isfile(clues_file_path)

    round_tripped_clues = movie_clues.read_movie_clues_file(clues_file_path)
    assert round_tripped_clues == clues_list
