import pandas as pd

import actorle_solver

import pytest

from movie_clues import MovieClue, movie_title_to_clues_pattern


@pytest.fixture()
def single_movie_dataframe():
    movie_data = {
        'tconst': ['tt0079501'],
        'primaryTitle': ['Mad Max'],
        'startYear': ['1979'],
        'averageRating': [6.8]
    }
    yield pd.DataFrame(data=movie_data), movie_data


def clue_that_should_be_matched(movie_dataframe):
    movies_list = movie_dataframe.to_dict('records')
    first_movie = movies_list[0]
    return MovieClue(
        movie_title_to_clues_pattern(first_movie['primaryTitle']),
        first_movie['startYear'],
        'Adventure,Action,Thriller,Science Fiction',  # whatevs, not used in matching
        first_movie['averageRating']
    )


def change_movie_rating_in_clue(clue_to_modify, rating_change):
    return MovieClue(
        clue_to_modify.title_pattern,
        clue_to_modify.year,
        clue_to_modify.genre_list,
        round(clue_to_modify.score + rating_change, 2),
    )


def test_matches_movie_with_exact_review_score_match(single_movie_dataframe):
    movie_data_frame, movie_data = single_movie_dataframe
    assert movie_data_frame.shape[0] == 1

    matched_movies_df = actorle_solver.get_matching_movies_dataframe(movie_data_frame,
                                                                     clue_that_should_be_matched(movie_data_frame),
                                                                     0.0)

    matches_list = matched_movies_df.to_dict('records')
    assert len(matches_list) == 1
    assert matches_list[0] == {
        'primaryTitle': movie_data['primaryTitle'][0],
        'tconst': movie_data['tconst'][0]
    }


def test_matches_movie_with_different_review_score_when_inside_tolerance(single_movie_dataframe):
    movie_data_frame, movie_data = single_movie_dataframe
    assert movie_data_frame.shape[0] == 1
    # make the rating score in the clue differ from the rating score in the movie data
    rating_tolerance = 0.1
    clue = change_movie_rating_in_clue(clue_that_should_be_matched(movie_data_frame), rating_tolerance)

    matched_movies_df = actorle_solver.get_matching_movies_dataframe(movie_data_frame, clue, rating_tolerance)

    matches_list = matched_movies_df.to_dict('records')
    assert len(matches_list) == 1
    assert matches_list[0] == {
        'primaryTitle': movie_data['primaryTitle'][0],
        'tconst': movie_data['tconst'][0]
    }


def test_does_not_match_movie_with_review_score_outside_tolerance(single_movie_dataframe):
    movie_data_frame, movie_data = single_movie_dataframe
    # make the rating score in the clue differ from the rating score in the movie data
    clue = change_movie_rating_in_clue(clue_that_should_be_matched(movie_data_frame), 0.1)

    matched_movies_df = actorle_solver.get_matching_movies_dataframe(movie_data_frame, clue, 0.0)

    matches_list = matched_movies_df.to_dict('records')
    assert len(matches_list) == 0
