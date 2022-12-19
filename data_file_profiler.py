import os
import sys
import tempfile
from datetime import datetime

import pandas as pd
from pandas_profiling import ProfileReport

if __name__ == '__main__':
    start_time = datetime.now()

    file_to_profile = sys.argv[1]
    file_short_name = os.path.basename(file_to_profile)
    separator = sys.argv[2]
    report_file_path = "{}/{}-profile.html".format(tempfile.gettempdir(), file_short_name)
    print("Profiling data file {} (separator = '{}'). Will write HTML report to {}."
          .format(file_to_profile,
                  separator,
                  report_file_path))

    df = pd.read_csv(file_to_profile, sep='\t')
    print("Finished reading data file into a dataframe")
    profile = ProfileReport(df, title="Pandas Profiling Report for {}".format(file_short_name))
    print("Finished making the profile object")
    profile.to_file(report_file_path)
    print("Finished writing the HTML report")

    end_time = datetime.now()
    duration=(end_time - start_time).seconds
    print("Finished in {} seconds".format(duration))