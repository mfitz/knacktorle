import argparse
import csv
import os
import subprocess

from datetime import datetime
from cli import SmartFormatter
from movie_clues import read_movie_clues_file

from rich.console import Console
from rich.table import Table

ELIDED_STRING = "********"


def read_expected_answers(answers_file_path):
    with open(answers_file_path) as answers_file:
        next(answers_file)  # Skip the header
        reader = csv.reader(answers_file, skipinitialspace=True)
        all_answers = dict(reader)
    return all_answers


def solve_puzzle(clues_file_path, solver_script_path, script_param_list):
    script_param_string = " ".join(script_param_list)
    shell_cmd = (
        "bash {} --clues-file {} {} | "
        "grep -i \"Dude - I think \" | "
        "awk -F \"Dude - I think it's... \" '{{print $NF}}' | "
        "awk -F '\\!' '{{print $1}}'".format(solver_script_path,
                                             clues_file_path,
                                             script_param_string))
    return subprocess.getoutput(shell_cmd)


def print_summary(start_datetime, puzzle_results_dict, elide_correct_answers):
    running_time = datetime.now() - start_datetime
    console = Console()
    console.print("")
    passes = [
        puzzle_details['result']
        for puzzle_details
        in puzzle_results_dict.values()
        if result == "PASS"
    ]
    failures = [
        puzzle_details['result']
        for puzzle_details
        in puzzle_results_dict.values()
        if result == "FAIL"
    ]
    unknown_results = len(puzzle_results_dict) - (len(failures) + len(passes))
    table_caption = "{} failed, {} passed, {} unknown in [yellow bold]{}[/yellow bold]" \
        .format(len(failures), len(passes), unknown_results, format_time_delta(running_time))
    results_table = Table(show_header=True,
                          header_style="bold magenta",
                          title="Summary",
                          caption=table_caption)
    results_table.add_column("Puzzle", justify="left")
    results_table.add_column("No. Clues", justify="center")
    results_table.add_column("Expected Answer", justify="left")
    results_table.add_column("Actual Answer", justify="left")
    results_table.add_column("Result", justify="left")
    results_table.add_column("Time", style="dim")
    for puzzle_name, puzzle_detail in puzzle_results_dict.items():
        short_name = puzzle_name.split('/')[-1]
        puzzle_expected_answer = puzzle_detail['expected_answer']
        solver_actual_answer = puzzle_detail['solver_answer']
        if puzzle_detail['result'] == "PASS" and elide_correct_answers:
            puzzle_expected_answer = ELIDED_STRING
            solver_actual_answer = ELIDED_STRING
        colour = "green" if puzzle_detail['result'] == "PASS" \
            else "red" if puzzle_detail['result'] == "FAIL" else "yellow"
        results_table.add_row(short_name,
                              str(puzzle_detail['number_of_clues']),
                              puzzle_expected_answer,
                              solver_actual_answer,
                              "[{}]{}[/{}]".format(colour, puzzle_detail['result'], colour),
                              format_time_delta(puzzle_detail['duration']))
    console.print(results_table)
    console.print("")


def format_time_delta(time_delta):
    return str(time_delta)[:-3]


def parse_cli_args():
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
    arg_parser.add_argument('-e',
                            '--elide-answers',
                            default=False,
                            action='store_true',
                            help="R|flag to elide puzzle answers for passing tests in the summary table\n"
                                 "Optional.")
    arg_parser.add_argument('-l',
                            '--param-list',
                            nargs='*',
                            default=[],
                            help='Optional list of parameters to pass to the solver script')
    return vars(arg_parser.parse_args())


if __name__ == '__main__':
    cli_args = parse_cli_args()

    print("Invoking the solver script at {}, with the param list '{}' "
          "to solve puzzles from the {} directory, and validating answers using the {} file"
          .format(cli_args['solver_script'],
                  cli_args['param_list'],
                  cli_args['puzzle_directory'],
                  cli_args['answers_file']))

    puzzle_results = {}
    for puzzle in sorted(os.listdir(cli_args['puzzle_directory'])):
        puzzle_path = os.path.join(cli_args['puzzle_directory'], puzzle)
        clues = read_movie_clues_file(puzzle_path)
        puzzle_results[puzzle] = {"number_of_clues": len(clues)}

    answers = read_expected_answers(cli_args['answers_file'])
    print("Read in {} expected answers from {} file...".format(len(answers), cli_args['answers_file']))
    print("-----------------------------------------------")

    solving_start_time = datetime.now()
    for puzzle in sorted(os.listdir(cli_args['puzzle_directory'])):
        puzzle_path = os.path.join(cli_args['puzzle_directory'], puzzle)
        expected_answer = answers.get(puzzle, "Unknown")
        expected_answer_to_show = ELIDED_STRING if cli_args['elide_answers'] else expected_answer
        print("Solving puzzle {} and expecting the answer '{}'".format(puzzle_path, expected_answer_to_show))
        puzzle_start_time = datetime.now()
        solver_answer = solve_puzzle(puzzle_path, cli_args['solver_script'], cli_args['param_list'])
        solver_answer_to_show = ELIDED_STRING if cli_args['elide_answers'] else solver_answer
        puzzle_duration = datetime.now() - puzzle_start_time
        print("Got answer '{}'".format(solver_answer_to_show))
        result = "N/A"
        if solver_answer == expected_answer:
            result = "PASS"
        elif expected_answer != "Unknown" and solver_answer != expected_answer:
            result = "FAIL"
        puzzle_results[puzzle]['expected_answer'] = expected_answer
        puzzle_results[puzzle]['solver_answer'] = solver_answer
        puzzle_results[puzzle]['result'] = result
        puzzle_results[puzzle]['duration'] = puzzle_duration
        print("-----------------------------------------------")
    print_summary(solving_start_time, puzzle_results, cli_args['elide_answers'])
