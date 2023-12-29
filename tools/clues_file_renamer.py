import os

import sys


months = {
    'jan': '01',
    'feb': '02',
    'mar': '03',
    'apr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'aug': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dec': '12',
}


if __name__ == '__main__':
    clues_file_dir = sys.argv[1]
    for clues_file in os.listdir(clues_file_dir):
        old_name = '{}/{}'.format(clues_file_dir, clues_file)
        new_name = old_name
        for month, number in months.items():
            new_name = new_name.replace(month, number)
        print("Going to rename '{}' to {}".format(old_name, new_name))
        os.rename(old_name, new_name)

