import sys

from movie_clues import parse_clues_from_html, write_movie_clues_file

if __name__ == '__main__':
    file_to_transform = sys.argv[1]
    print("Transforming the raw actorle HTML content from {}...".format(file_to_transform))

    with open(file_to_transform, "r") as raw_file:
        raw_content = raw_file.read()
    clues = parse_clues_from_html(raw_content)
    write_movie_clues_file(file_to_transform, clues)

    print("Transformed {} into a knacktorle clues file".format(file_to_transform))
