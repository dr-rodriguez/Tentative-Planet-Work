# Read the data from the csv file and compare against APT/VSR information

import pandas as pd
from trexolists.get_summary import summary_info


def read_data(file_path):
    df = pd.read_csv(file_path)
    return df


if __name__ == "__main__":
    df = read_data("data/03_trexolists_extended.csv")
    print(df.head())

    target_name = "WASP-96"
    planet_letter = "b"
    proposal_id = 2734
    summary_info = summary_info(proposal_id, target_name, planet_letter)
    print(summary_info)