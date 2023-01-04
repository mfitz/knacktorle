import argparse
import collections
import pprint
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from chromedriver_py import binary_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


@dataclass(eq=True, frozen=True)
class MovieClue:
    title_pattern: str
    year: str
    genre_list: str
    score: float


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
    return vars(arg_parser.parse_args())


def get_todays_clues_from_website():
    def movie_clues_grouper(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    url = 'https://actorle.com/'
    print("Requesting {} via selenium".format(url))
    service_object = Service(binary_path)
    driver_options = Options()
    driver_options.headless = True
    driver = webdriver.Chrome(service=service_object, options=driver_options)
    driver.get(url)
    print("Retrieved page with title '{}'".format(driver.title))

    elem = driver.find_element(By.TAG_NAME, 'table')
    all_clue_parts = elem.text.split('\n')[2:]
    movies_to_find = []
    # TODO: fix the genre list parsing - genres are being concatenated into a single word
    for movie_parts in movie_clues_grouper(all_clue_parts, 4):
        movie_to_find = MovieClue(title_pattern=movie_parts[0].strip(),
                                  year=movie_parts[1],
                                  genre_list=movie_parts[2].strip(),
                                  score=float(movie_parts[3].strip()))
        movies_to_find.append(movie_to_find)
    return movies_to_find


def get_actors_in_movies(actors_dataframe, movie_ids):
    matching_actors = actors_dataframe[actors_dataframe.tconst.isin(movie_ids.tconst)]
    print("Found {} actors for these {} movie_ids".format(matching_actors.shape[0], len(movie_ids)))
    return matching_actors[['nconst', 'characters']]


def make_regex(movie_title_pattern):
    words = movie_title_pattern.split()
    regex_pattern = ""
    character_pattern = "[a-zA-Z0-9:\\'&-]"
    for index, word in enumerate(words):
        regex_pattern += "{}{{{}}}".format(character_pattern, len(word))
        if index != len(words) - 1:
            regex_pattern += " "
    regex_pattern += "$"
    return regex_pattern


def get_matching_movie_ids(titles_data_frame, movie_clue):
    match_pattern = make_regex(movie_clue.title_pattern)
    query = "originalTitle.str.match('{}') and startYear == \"{}\"".format(match_pattern, movie_clue.year)
    print("Querying movies data frame with {}".format(query))
    results = titles_data_frame.query(query)
    print("{} Matches for pattern '{}', year {}".format(results.shape[0], movie_clue.title_pattern, movie_clue.year))
    return results[['tconst', 'primaryTitle', 'genres']]


def filter_movies(movies_file, movies_clues):
    titles_data_frame = pd.read_csv(movies_file, sep='\t')
    pd.set_option('display.max_columns', None)

    print("Read in {} titles - filtering out non-movies...".format(titles_data_frame.shape[0]))
    titles_data_frame = titles_data_frame[titles_data_frame.titleType == "movie"]
    print("Filtered down to {} movie titles".format(titles_data_frame.shape[0]))

    movie_years = set([mv.year for mv in movies_clues])
    print("Filtering out movies NOT from the years {}".format(movie_years))
    titles_data_frame = titles_data_frame[titles_data_frame.startYear.isin(movie_years)]
    print("Filtered down to {} movie titles".format(titles_data_frame.shape[0]))

    return titles_data_frame


def get_all_performances(actors_data_file):
    actors_data_frame = pd.read_csv(actors_data_file, sep='\t')
    print("Read in data on {} performances".format(actors_data_frame.shape[0]))
    return actors_data_frame


def write_movie_clues(clues_file_path, clues):
    print("Writing movie clues out to {}".format(clues_file_path))
    with open(clues_file_path, 'w') as clues_file:
        for clue in clues:
            genres = ''.join(clue.genre_list)
            clues_file.write("{}|{}|{}|{}\n".format(clue.title_pattern, clue.year, genres, clue.score))


def read_movie_clues(clues_file_path):
    print("Reading movie clues in from {}".format(clues_file_path))
    with open(clues_file_path) as clues_file:
        movie_clues = clues_file.readlines()
    movies_to_find = []
    for movie in movie_clues:
        movie_data = movie.split("|")
        movie_to_find = MovieClue(title_pattern=movie_data[0].strip(),
                                  year=movie_data[1],
                                  genre_list=movie_data[2].strip(),
                                  score=float(movie_data[3].strip()))
        movies_to_find.append(movie_to_find)
    return movies_to_find


def get_most_likely_actors_for_clues(puzzle_clues, movies_data_frame, performances_df):
    print("\nWorking through the clues...")
    all_potential_performances = []
    for clue in puzzle_clues:
        print("Looking for movie matches for {}".format(clue))
        matching_movies = get_matching_movie_ids(movies_data_frame, clue)
        actors_ids = get_actors_in_movies(performances_df, matching_movies)
        all_potential_performances.extend(actors_ids.nconst.tolist())
    print("Made a list of {} individual movie performances from all the clues".format(len(all_potential_performances)))
    return collections.Counter(all_potential_performances).most_common(3)


def read_clues(puzzle):
    if puzzle:
        print("Solving the puzzle contained in {}".format(puzzle))
        clues = read_movie_clues(puzzle)
    else:
        print("No puzzle file supplied - will solve today's puzzle on https://actorle.com/")
        puzzle = datetime.today().strftime('%Y-%m-%d')
        clues = get_todays_clues_from_website()
    print("Found {} clues for the puzzle for {}".format(len(clues), puzzle))
    pprint.pprint(clues)
    return clues


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

    puzzle_clues = read_clues(args['clues_file'])
    if args['write_clues_file']:
        write_movie_clues(args['write_clues_file'], puzzle_clues)

    movies_file = args['movies_file']
    print("Using IMDd movie data in {}".format(movies_file))
    movies_df = filter_movies(movies_file, puzzle_clues)

    performances_file = args['performances_file']
    print("Using IMDd performances data in {}".format(performances_file))
    performances_df = get_all_performances(performances_file)

    most_likely_actors = get_most_likely_actors_for_clues(puzzle_clues, movies_df, performances_df)
    print("Actor IDs occurring most often across all possible candidate movies:{}".format(most_likely_actors))
    total_count = sum(count for actor_id, count in most_likely_actors)

    actors_file = args['actors_file']
    print("Converting actor IDs to names using {}".format(actors_file))
    actor_names_df = pd.read_csv(actors_file, sep='\t')

    actor = most_likely_actors[0][0]
    actor_name = get_actor_name(actor, actor_names_df)
    print("\nDude - I think it's... {}!\n".format(actor_name))
    print("Here are some {} film roles that match the movie titles in the clues:\n".format(actor_name))
    actor_roles = get_matching_movies_for_actor(puzzle_clues, actor, performances_df, movies_df)
    pd.set_option('display.width', 1000)
    print(actor_roles)
    print("\nOptions\n----------------")
    for actor_id, count in most_likely_actors:
        actor_name = get_actor_name(actor_id, actor_names_df)
        percent_likelihood = (count / total_count) * 100.0
        print("\t{} is {:.2f}% likely".format(actor_name, percent_likelihood))
