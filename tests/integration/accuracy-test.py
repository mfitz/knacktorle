import argparse
import csv
import os
import subprocess

from cli import SmartFormatter


def read_expected_answers(answers_file_path):
    with open(answers_file_path) as answers_file:
        next(answers_file)  # Skip the header
        reader = csv.reader(answers_file, skipinitialspace=True)
        all_answers = dict(reader)
    return all_answers


def solve_puzzle(clues_file_path, solver_script_path):
    shell_cmd = (
        "bash {} --clues-file {} | "
        "grep -i dude | "
        "awk -F \"Dude - I think it's... \" '{{print $NF}}' | "
        "awk -F '\\!' '{{print $1}}'".format(solver_script_path, clues_file_path))
    return subprocess.getoutput(shell_cmd)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description="Solve a set of puzzles from a directory of clues files,"
                    "compare the answers to a set of correct answers and"
                    " provide an accuracy rating based on the aggregate comparison",
        formatter_class=SmartFormatter)
    arg_parser.add_argument('-p',
                            '--puzzle-directory',
                            help="R|the full path to directory containing clues files\n"
                                 "Mandatory.",
                            required=True)
    arg_parser.add_argument('-a',
                            '--answers-file',
                            help="R|the full path to a CSV file containing answers to puzzles\n"
                                 "Mandatory.",
                            required=True)
    arg_parser.add_argument('-s',
                            '--solver-script',
                            help="R|the full path to a shell script that solves a single puzzle\n"
                                 "Mandatory.",
                            required=True)
    cli_args = vars(arg_parser.parse_args())

    print("Solving puzzles from the {} directory, and validating answers using the {} file"
          .format(cli_args['puzzle_directory'], cli_args['answers_file']))

    print("Reading in expected answers from {} file...".format(cli_args['answers_file']))
    answers = read_expected_answers(cli_args['answers_file'])

    for puzzle in os.listdir(cli_args['puzzle_directory']):
        puzzle_path = os.path.join(cli_args['puzzle_directory'], puzzle)
        expected_answer = answers[puzzle]
        print("Solving puzzle {} and expecting the answer '{}'".format(puzzle_path, expected_answer))
        solver_answer = solve_puzzle(puzzle_path, cli_args['solver_script'])
        print("Got answer '{}'".format(solver_answer))
        print("-----------------------------------------------")
