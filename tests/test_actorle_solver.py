import pandas as pd

import actorle_solver

from movie_clues import MovieClue


def test_matches_movie_with_exact_review_rating_match():
    clue = MovieClue('xxx xxx', '1979', 'Adventure,Action,Thriller,Science Fiction', 6.8)
    movie_data = {
        'tconst': ['tt0079501'],
        'primaryTitle': ['Mad Max'],
        'startYear': ['1979'],
        'averageRating': [6.8]
    }
    titles_dataframe = pd.DataFrame(data=movie_data)

    matched_movies = actorle_solver.get_matching_movie_ids(titles_dataframe, clue, 0.0)

    assert matched_movies.to_dict() == {
        'primaryTitle': {0: 'Mad Max'},
        'tconst': {0: 'tt0079501'}
    }


def test_matches_movie_with_review_rating_just_inside_tolerance():
    clue = MovieClue('xxx xxx', '1979', 'Adventure,Action,Thriller,Science Fiction', 6.9)
    movie_data = {
        'tconst': ['tt0079501'],
        'primaryTitle': ['Mad Max'],
        'startYear': ['1979'],
        'averageRating': [6.8]
    }
    titles_dataframe = pd.DataFrame(data=movie_data)

    matched_movies = actorle_solver.get_matching_movie_ids(titles_dataframe, clue, 0.1)

    assert matched_movies.to_dict() == {
        'primaryTitle': {0: 'Mad Max'},
        'tconst': {0: 'tt0079501'}
    }
