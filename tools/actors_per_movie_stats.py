import sys

import pandas as pd

if __name__ == '__main__':
    movies_actors_file = sys.argv[1]
    print("Generating actors-per-movie stats from {}".format(movies_actors_file))

    print('Reading the data...')
    actors_data_frame = pd.read_csv(movies_actors_file, sep='\t')
    print('Read in {} rows of data'.format(actors_data_frame.shape[0]))

    stats = actors_data_frame.groupby('tconst').count().describe(percentiles=[0.25, 0.5, 0.75, 0.9]).nconst
    print(stats)
    print("\nFound {} distinct movies".format(stats['count']))
    print("\nActors per Movie")
    print("------------------------------")
    print("Min: {}".format(stats['min']))
    print("Max: {}".format(stats['max']))
    print("Mean: {:.2f} (SD: {:.2f})".format(stats['mean'], stats['std']))
    print("25th percentile: {}".format(stats['25%']))
    print("50th percentile: {}".format(stats['50%']))
    print("75th percentile: {}".format(stats['75%']))
    print("90th percentile: {}".format(stats['90%']))
