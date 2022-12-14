import argparse
import hashlib
import os
import pathlib
import shutil

import pandas as pd
import requests
from rich.progress import Progress, BarColumn

from actorle_solver import SmartFormatter


def parse_args():
    arg_parser = argparse.ArgumentParser(description="Download and filter data files from "
                                                     "https://datasets.imdbws.com. The files to be grabbed are: "
                                                     "title.basics.tsv.gz, "
                                                     "title.principals.tsv.gz, "
                                                     "name.basics.tsv.gz",
                                         formatter_class=SmartFormatter)
    arg_parser.add_argument('-o',
                            '--output-dir',
                            help="R|the full path to a local directory to write the downloaded files to.\n"
                                 "Mandatory.",
                            required=True)
    return vars(arg_parser.parse_args())


def file_md5(file_path):
    return hashlib.md5(pathlib.Path(file_path).read_bytes()).hexdigest()


def download_file(local_path, url):
    print("Looking for {}...".format(local_path))
    if not pathlib.Path.exists(pathlib.Path(local_path)):
        print("\t{} Not found".format(local_path))
        with Progress("\tDownloading {}".format(url), BarColumn(), transient=True) as progress:
            task = progress.add_task("Downloading", start=False)
            with requests.get(url, stream=True) as r:
                with open(local_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            progress.update(task)
        print("\tDownloaded {}".format(url))
        return True
    else:
        print("\t{} already exists with eTag {} - will not download".format(local_path, file_md5(local_path)))
        return False


def filter_movies_file(movies_file_path):
    print("\tFiltering {}".format(movies_file_path))
    movies_data_frame = pd.read_csv(movies_file_path, sep='\t')

    print("\tRead in {:,} rows - filtering out non-movies...".format(movies_data_frame.shape[0]))
    movies_data_frame = movies_data_frame[movies_data_frame.titleType == "movie"]
    print("\tFiltered down to {:,} movie titles, writing new file to {}".format(movies_data_frame.shape[0],
                                                                                movies_file_path))

    movies_data_frame.to_csv(movies_file_path, sep='\t', compression='gzip', index=False)
    print("\tWritten filtered file to {}".format(movies_file_path))
    return movies_data_frame


def filter_actors_file(actors_file_path):
    print("\tFiltering {}".format(actors_file_path))
    actors_data_frame = pd.read_csv(actors_file_path, sep='\t')

    print("\tRead in {:,} rows - filtering out non-actors...".format(actors_data_frame.shape[0]))
    actors_data_frame = actors_data_frame[(actors_data_frame.primaryProfession.str.contains("actor")) |
                                          (actors_data_frame.primaryProfession.str.contains("actress"))]
    print("\tFiltered down to {:,} actors, writing new file to {}".format(actors_data_frame.shape[0], actors_file_path))

    actors_data_frame.to_csv(actors_file_path, sep='\t', compression='gzip', index=False)
    print("\tWritten filtered file to {}".format(actors_file_path))


def filter_performances_file(performances_file_path, movies_dataframe=None):
    print("\tFiltering {}".format(performances_file_path))
    performances_data_frame = pd.read_csv(performances_file_path, sep='\t')

    print("\tRead in {:,} rows - filtering out non-acting categories...".format(performances_data_frame.shape[0]))
    performances_data_frame = \
        performances_data_frame[(performances_data_frame.category == "actor") |
                                (performances_data_frame.category == "actress")]
    print("\tRemoved non-acting categories - we now have {:,} rows".format(performances_data_frame.shape[0]))
    if movies_dataframe is not None:
        print("\tFiltering out performances in non-movies using movies dataframe containing {:,} movies"
              .format(movies_dataframe.shape[0]))
        performances_data_frame = \
            performances_data_frame[performances_data_frame.tconst.isin(movies_dataframe.tconst)]

    print("\tFiltered down to {:,} movie performances - writing new file out to {}"
          .format(performances_data_frame.shape[0], performances_file_path))
    performances_data_frame.to_csv(performances_file_path, sep='\t', compression='gzip', index=False)
    print("\tFinished writing filtered file to {}".format(performances_file_path))


if __name__ == '__main__':
    args = parse_args()
    data_dir = args['output_dir']
    print("Updating IMDb data files in {} directory".format(data_dir))

    base_url = "https://datasets.imdbws.com"

    movies_file = 'title.basics.tsv.gz'
    movies_df = None
    local_movies_file = os.path.abspath(os.path.join(data_dir, movies_file))
    print('-----------------------------------')
    if download_file(local_movies_file, "{}/{}".format(base_url, movies_file)):
        movies_df = filter_movies_file(local_movies_file)

    performances_file = 'title.principals.tsv.gz'
    local_performances_file = os.path.abspath(os.path.join(data_dir, performances_file))
    print('-----------------------------------')
    if download_file(local_performances_file, "{}/{}".format(base_url, performances_file)):
        filter_performances_file(local_performances_file, movies_dataframe=movies_df)

    actors_file = 'name.basics.tsv.gz'
    local_actors_file = os.path.abspath(os.path.join(data_dir, actors_file))
    print('-----------------------------------')
    if download_file(local_actors_file, "{}/{}".format(base_url, actors_file)):
        filter_actors_file(local_actors_file)
