import pprint
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


@dataclass(eq=True, frozen=True)
class MovieClue:
    title_pattern: str
    year: str
    genre_list: str
    score: float


def write_movie_clues_file(clues_file_path, clues):
    print("Writing movie clues out to {}".format(clues_file_path))
    with open(clues_file_path, 'w') as clues_file:
        for clue in clues:
            genres = ''.join(clue.genre_list)
            clues_file.write("{}|{}|{}|{}\n".format(clue.title_pattern, clue.year, genres, clue.score))


def read_movie_clues_file(clues_file_path):
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


def get_todays_clues_from_website():
    url = 'https://actorle.com/'
    print("Requesting {} via selenium".format(url))
    service_object = Service(binary_path)
    driver_options = Options()
    driver_options.headless = True
    driver = webdriver.Chrome(service=service_object, options=driver_options)
    driver.get(url)
    print("Retrieved a web page with the title '{}'".format(driver.title))
    return parse_clues_from_html(driver.page_source)


def parse_clues_from_html(clues_html):
    soup = BeautifulSoup(clues_html, 'html.parser')
    clues_table = soup.find('table')
    clues_rows = clues_table.find_all('tr')[1:]

    clues_list = []
    for row in clues_rows:
        row_cells = row.find_all('td')
        movie_title_pattern = row_cells[0].find_all('div')[0].text
        movie_release_year = row_cells[0].find_all('div')[1].text
        movie_genres = []
        movie_genres_spans = row_cells[1].find_all('span')
        for span in movie_genres_spans:
            movie_genres.append(span.text)
        movie_score = row_cells[2].text
        clues_list.append(MovieClue(movie_title_pattern.replace('\u2002', ' ').replace('×', 'x'),
                                    movie_release_year,
                                    ','.join(movie_genres),
                                    float(movie_score)))
    return clues_list


def read_puzzle_clues(puzzle):
    if puzzle:
        print("Solving the puzzle contained in the clues file at {}".format(puzzle))
        clues = read_movie_clues_file(puzzle)
    else:
        print("No clues file supplied; solving today's puzzle from https://actorle.com/")
        puzzle = datetime.today().strftime('%Y-%m-%d')
        clues = get_todays_clues_from_website()
    print("Found {} clues for the puzzle from {}:".format(len(clues), puzzle))
    pprint.pprint(clues)
    return clues


def make_movie_title_regex(movie_title_pattern):
    words = movie_title_pattern.split()
    regex_pattern = ""
    for index, word in enumerate(words):
        regex_pattern += make_movie_title_word_regex(word)
        if index != len(words) - 1:
            regex_pattern += " "
    regex_pattern += "$"
    return regex_pattern


def make_movie_title_word_regex(movie_title_word):
    alnum_character_count = 0
    alnum_character_pattern = "\\w"
    word_regex = ''
    for character in movie_title_word:
        if character.isalnum():
            alnum_character_count += 1
        else:
            if alnum_character_count != 0:
                word_regex += "{}{{{}}}".format(alnum_character_pattern, alnum_character_count)
            word_regex += "\\{}".format(character)
            alnum_character_count = 0
    if alnum_character_count != 0:
        word_regex += "{}{{{}}}".format(alnum_character_pattern, alnum_character_count)
    return word_regex


def movie_title_to_clues_pattern(movie_title):
    pattern = ''
    for character in movie_title:
        if character.isalnum():
            pattern += 'x'
        else:
            pattern += character
    return pattern
