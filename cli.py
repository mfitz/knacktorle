import argparse


# allows the use of newlines inside help screen text
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_cli_args():
    arg_parser = argparse.ArgumentParser(description="Solve an Actorle puzzle. Today's puzzle will be retrieved from "
                                                     "https://actorle.com/ and solved, unless a different puzzle is "
                                                     "specified using the --clues-file argument.",
                                         formatter_class=SmartFormatter)
    arg_parser.add_argument('-mf',
                            '--movies-file',
                            help="R|the full path to an IMDb title.basics.tsv.gz file, as modified by the\n"
                                 "data grabber tool imdb_data_grabber.py using raw data downloaded from\n"
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
                            type=int,
                            default=3)
    arg_parser.add_argument('-r',
                            '--rating-tolerance',
                            help='R|The tolerance around movie review rating matching. Optional, default is 0.1,\n'
                                 'meaning a clue with an IMDb score of 6.4 will match movies with scores from\n'
                                 '6.3 to 6.5 inclusive. This mechanism exists because IMDb scores can change over\n'
                                 'time as more people provide review scores.',
                            type=float,
                            default=0.1)
    return vars(arg_parser.parse_args())
