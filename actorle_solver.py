import argparse
import collections

import pandas as pd

from cli import SmartFormatter
from movie_clues import write_movie_clues_file, read_puzzle_clues


def parse_args():
    arg_parser = argparse.ArgumentParser(description="Solve an Actorle puzzle. Today's puzzle will be retrieved from "
                                                     "https://actorle.com/ and solved, unless a different puzzle is "
                                                     "specified using the --clues-file argument.",
                                         formatter_class=SmartFormatter)
    arg_parser.add_argument('-mf',
                            '--movies-file',
                            help="R|the full path to an IMDb title.basics.tsv.gz file, as found at "
                                 "https://datasets.imdbws.com.\n"
                                 "Mandatory.",
                            required=True)
    arg_parser.add_argument('-af',
                            '--actors-file',
                            help="R|the full path to an IMDb name.basics.tsv.gz file, as found at "
                                 "https://datasets.imdbws.com.\n"
                                 "Mandatory.",
                            required=True)
    arg_parser.add_argument('-pf',
                            '--performances-file',
                            help="R|the full path to an IMDb title.principals.tsv.gz file, as found at "
                                 "https://datasets.imdbws.com.\n"
                                 "Mandatory.",
                            required=True)
    arg_parser.add_argument('-cf',
                            '--clues-file',
                            help="R|the full path to a puzzle file that contains the clues. Optional.\nWhen this "
                                 "parameter is not set, today's puzzle will be retrieved from https://actorle.com/.\n"
                                 "Each line in the file represents the clues for an individual movie and should look "
                                 "like:\n\n"
                                 "<title pattern>|<year>|<genres>|<score>\n\n"
                                 "For example:\n\n"
                                 "xxx xxxxxxxxxxx|2002|Action,Crime,Thriller|7.1")
    arg_parser.add_argument('-w',
                            '--write-clues-file',
                            help='R|the full path to write out a puzzle file that contains the clues. Optional.\n'
                                 'This allows you to "save" puzzles to be used later/offline.\n'
                                 'Each line in the file represents the clues for '
                                 'an individual movie and will look like:\n\n'
                                 '<title pattern>|<year>|<genres>|<score>\n\n'
                                 'For example:\n\n'
                                 'xxx xxxxxxxxxxx|2002|Action,Crime,Thriller|7.1')
    arg_parser.add_argument('-n',
                            '--num-options',
                            help='The number of potential answers to display. Optional, default is 3.',
                            type=int)
    return vars(arg_parser.parse_args())


def get_actors_in_movies(performances_dataframe, movie_ids):
    matching_actors = performances_dataframe[performances_dataframe.tconst.isin(movie_ids.tconst)]
    print("Found {} actors for these {} movie_ids".format(matching_actors.shape[0], len(movie_ids)))
    return matching_actors[['nconst', 'characters']]


def make_regex(movie_title_pattern):
    words = movie_title_pattern.split()
    regex_pattern = ""
    character_pattern = "[a-zA-Z0-9:\\'&-\.]"
    for index, word in enumerate(words):
        regex_pattern += "{}{{{}}}".format(character_pattern, len(word))
        if index != len(words) - 1:
            regex_pattern += " "
    regex_pattern += "$"
    return regex_pattern


def get_matching_movie_ids(titles_data_frame, movie_clue):
    titles_data_frame = titles_data_frame[titles_data_frame.startYear == movie_clue.year]
    print("Filtered down to {} movies from the year {}".format(titles_data_frame.shape[0], movie_clue.year))
    match_pattern = make_regex(movie_clue.title_pattern)
    query = "primaryTitle.str.match('{}')".format(match_pattern)
    print("Filtering remaining movies with query '{}'".format(query))
    results = titles_data_frame.query(query)
    sample_size = min(results.shape[0], 3)
    print("{} Matches for pattern '{}', year {} (Sample: {})"
          .format(results.shape[0],
                  movie_clue.title_pattern,
                  movie_clue.year,
                  results['primaryTitle'].sample(n=sample_size).to_list()))
    return results[['tconst', 'primaryTitle']]


def filter_movies_by_release_date(movies_file, movies_clues):
    print("Reading movies in from {}...".format(movies_file))
    titles_data_frame = pd.read_csv(movies_file, sep='\t')
    pd.set_option('display.max_columns', None)
    print("Read in {:,} titles".format(titles_data_frame.shape[0]))

    movie_years = set([mv.year for mv in movies_clues])
    print("Filtering out movies NOT from the years {}...".format(movie_years))
    titles_data_frame = titles_data_frame[titles_data_frame.startYear.isin(movie_years)]
    print("Filtered down to {:,} movie titles".format(titles_data_frame.shape[0]))

    return titles_data_frame


def get_candidate_performances(performances_data_file, movies_df):
    actors_data_frame = pd.read_csv(performances_data_file, sep='\t')
    print("Read in data on {:,} performances".format(actors_data_frame.shape[0]))

    print("Filtering out performances NOT in one of the {:,} candidate movies...".format(movies_df.shape[0]))
    actors_data_frame = actors_data_frame[actors_data_frame.tconst.isin(movies_df.tconst)]
    print("Filtered down to {:,} performances".format(actors_data_frame.shape[0]))

    return actors_data_frame


def get_most_likely_actors_for_clues(puzzle_clues, movies_data_frame, performances_df, num_options):
    print("\nWorking through the clues...")
    all_potential_performances = []
    for clue in puzzle_clues:
        print('----------------------------')
        print("Looking for movie matches for {}".format(clue))
        matching_movies = get_matching_movie_ids(movies_data_frame, clue)
        actors_ids = get_actors_in_movies(performances_df, matching_movies)
        all_potential_performances.extend(actors_ids.nconst.tolist())
    print('----------------------------')
    print("Made a list of {:,} individual movie performances from all the clues"
          .format(len(all_potential_performances)))
    return collections.Counter(all_potential_performances).most_common(num_options)


def get_actor_name(actor_id, actor_names_df):
    return actor_names_df[actor_names_df.nconst == actor_id].iloc[0]['primaryName']


def title_to_pattern(movie_title):
    pattern = ''
    for character in movie_title:
        if character.isalnum():
            pattern += 'x'
        else:
            pattern += character
    return pattern


def get_matching_movies_for_actor(movie_clues, actor_id, performances_df, movies_df):
    all_actor_performances = performances_df[performances_df.nconst == actor_id][['tconst', 'characters']]
    actor_movies = \
        movies_df[movies_df.tconst.isin(all_actor_performances['tconst'])][['tconst', 'primaryTitle', 'startYear']]
    actor_movies = pd.merge(all_actor_performances, actor_movies, on=['tconst'])
    clue_title_patterns = set([clue.title_pattern for clue in movie_clues])
    filtered_movie_titles = [title for title in actor_movies['primaryTitle'].tolist()
                             if title_to_pattern(title) in clue_title_patterns]
    actor_movies = actor_movies[actor_movies['primaryTitle'].isin(filtered_movie_titles)][['primaryTitle',
                                                                                           'startYear',
                                                                                           'characters']]
    actor_movies = actor_movies.rename(columns=
    {
        'primaryTitle': 'Movie',
        'startYear': 'Year',
        'characters': 'Character'
    })
    return actor_movies.sort_values(by=['Year']).reset_index(drop=True)


if __name__ == '__main__':
    args = parse_args()

    puzzle_clues = read_puzzle_clues(args['clues_file'])
    if args['write_clues_file']:
        write_movie_clues_file(args['write_clues_file'], puzzle_clues)

    movies_file = args['movies_file']
    print("Reading IMDb movie data from {}".format(movies_file))
    movies_df = filter_movies_by_release_date(movies_file, puzzle_clues)

    performances_file = args['performances_file']
    print("Reading IMDb actor performances data from {}".format(performances_file))
    performances_df = get_candidate_performances(performances_file, movies_df)

    number_of_potential_matches = args['num_options']
    if not number_of_potential_matches:
        number_of_potential_matches = 3
    most_likely_actors = get_most_likely_actors_for_clues(puzzle_clues,
                                                          movies_df,
                                                          performances_df,
                                                          number_of_potential_matches)
    print("Actor IDs occurring most often across all possible candidate movies:{}".format(most_likely_actors))
    total_count = sum(count for actor_id, count in most_likely_actors)

    actors_file = args['actors_file']
    print("Converting actor IDs to names using {}".format(actors_file))
    actor_names_df = pd.read_csv(actors_file, sep='\t')

    actor = most_likely_actors[0][0]
    actor_name = get_actor_name(actor, actor_names_df)
    print("\n\nDude - I think it's... {}!".format(actor_name))
    print("Here are some {} film roles from movies that match clues:\n".format(actor_name))
    actor_roles = get_matching_movies_for_actor(puzzle_clues, actor, performances_df, movies_df)
    pd.set_option('display.width', 1000)
    print(actor_roles)
    print("\n\tOptions\n\t----------------")
    option_num = 1
    for actor_id, count in most_likely_actors:
        actor_name = get_actor_name(actor_id, actor_names_df)
        percent_likelihood = (count / total_count) * 100.0
        print("\t{}) {} is {:.2f}% likely".format(option_num, actor_name, percent_likelihood))
        option_num += 1
