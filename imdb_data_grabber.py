import argparse
import os
import hashlib
import pathlib
import requests
import shutil

from os.path import abspath

from rich.progress import Progress, BarColumn


def file_md5(file_path):
    return hashlib.md5(pathlib.Path(file_path).read_bytes()).hexdigest()


def download_file(local_path, url, eTag=None):
    #         with Progress("  Pulling {}{}{}".format(Fore.YELLOW, ecr_image, Style.RESET_ALL),
    #                       BarColumn(),
    #                       transient=True) as progress:
    #             task = progress.add_task("Pulling", start=False)
    #             repo_name = ecr_image.split(':')[0]
    #             image_tag = ecr_image.split(':')[1]
    #             docker_client.images.pull(repository=repo_name,
    #                                       tag=image_tag,
    #                                       auth_config={'username': user, 'password': pw})
    #             progress.update(task)
    with Progress("\tDownloading {}".format(url), BarColumn(), transient=True) as progress:
        task = progress.add_task("Downloading", start=False)
        with requests.get(url, stream=True) as r:
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        progress.update(task)


if __name__ == '__main__':
    data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
    print("Updating IMDB data files in {}".format(data_dir))

    required_files = ['title.basics.tsv.gz', 'title.principals.tsv.gz', 'name.basics.tsv.gz']
    for file in required_files:
        file_path = os.path.abspath(os.path.join(data_dir, file))
        etag = None
        print("\tLooking for {}".format(file_path))
        if not pathlib.Path.exists(pathlib.Path(file_path)):
            print("\t{} does not exist - downloading it now...".format(file_path))
        else:
            etag = file_md5(file_path)
            print("\t{} exists with eTag {}".format(file_path, etag))
        url = "https://datasets.imdbws.com/{}".format(file)
        download_file(file_path, url, eTag=etag)
        # https://datasets.imdbws.com/title.ratings.tsv.gz
