import argparse
import hashlib
import os
import pathlib
import shutil

import requests
from rich.progress import Progress, BarColumn

from actorle_solver import SmartFormatter


def parse_args():
    arg_parser = argparse.ArgumentParser(description="Download and/or filter data files from "
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


def download_file(local_path, url, eTag=None):
    print("\tLooking for {}".format(local_path))
    if not pathlib.Path.exists(pathlib.Path(local_path)):
        print("\t{} Not found".format(local_path))
        with Progress("\tDownloading {}".format(url), BarColumn(), transient=True) as progress:
            task = progress.add_task("Downloading", start=False)
            with requests.get(url, stream=True) as r:
                with open(local_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            progress.update(task)
    else:
        etag = file_md5(local_path)
        print("\t{} exists with eTag {} - will not download".format(file_path, etag))


if __name__ == '__main__':
    args = parse_args()
    data_dir = args['output_dir']
    print("Updating IMDd data files in {}".format(data_dir))

    required_files = ['title.basics.tsv.gz', 'title.principals.tsv.gz', 'name.basics.tsv.gz']
    for file in required_files:
        file_path = os.path.abspath(os.path.join(data_dir, file))
        etag = None
        url = "https://datasets.imdbws.com/{}".format(file)
        download_file(file_path, url, eTag=etag)
