import argparse
import csv
import os
import subprocess

from datetime import datetime
from cli import SmartFormatter

from rich.console import Console
from rich.table import Table


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


def print_summary(start_datetime, puzzle_results_dict):
    console = Console()
    console.print("")
    passes = [
        result
        for expected_answer, solver_answer, result, duration
        in puzzle_results_dict.values()
        if result == "PASS"
    ]
    failures = [
        result
        for expected_answer, solver_answer, result, duration
        in puzzle_results_dict.values()
        if result == "FAIL"
    ]
    table_caption = "{} failed, {} passed in [yellow bold]{}[/yellow bold]" \
        .format(len(failures),
                len(passes),
                format_time_delta(datetime.now() - start_datetime))
    results_table = Table(show_header=True,
                          header_style="bold magenta",
                          title="Summary",
                          caption=table_caption)
    results_table.add_column("Puzzle", justify="left")
    results_table.add_column("Expected Answer", justify="left")
    results_table.add_column("Actual Answer", justify="left")
    results_table.add_column("Result", justify="left")
    results_table.add_column("Time", style="dim")
    for puzzle_name, result in puzzle_results_dict.items():
        short_name = puzzle_name.split('/')[-1]
        expected_answer, solver_answer, outcome, duration = result
        colour = "green" if outcome == "PASS" else "red"
        results_table.add_row(short_name,
                              expected_answer,
                              solver_answer,
                              "[{}]{}[/{}]".format(colour, outcome, colour),
                              format_time_delta(duration))
    console.print(results_table)
    console.print("")


def format_time_delta(time_delta):
    return (str(time_delta))[:-3]


if __name__ == '__main__':
    start_time = datetime.now()
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
    print("-----------------------------------------------")
    answers = read_expected_answers(cli_args['answers_file'])

    puzzle_results = {}
    for puzzle in os.listdir(cli_args['puzzle_directory']):
        puzzle_path = os.path.join(cli_args['puzzle_directory'], puzzle)
        expected_answer = answers.get(puzzle, "Unknown")
        print("Solving puzzle {} and expecting the answer '{}'".format(puzzle_path, expected_answer))
        start_time = datetime.now()
        solver_answer = solve_puzzle(puzzle_path, cli_args['solver_script'])
        duration = datetime.now() - start_time
        print("Got answer '{}'".format(solver_answer))
        result = "N/A"
        if solver_answer == expected_answer:
            result = "PASS"
        elif expected_answer != "Unknown" and solver_answer != expected_answer:
            result = "FAIL"
        puzzle_results[puzzle] = (expected_answer, solver_answer, result, duration)
        print("-----------------------------------------------")
    print_summary(start_time, puzzle_results)
