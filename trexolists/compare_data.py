# Read the data from the csv file and compare against APT/VSR information

import pandas as pd
from trexolists.get_summary import gather_summary_info


def read_data(file_path):
    df = pd.read_csv(file_path)
    return df


def compare_values(df, summary_dict):
    # Get the corresponding row in the dataframe
    row = df[(df['hostname_nn'] == summary_dict['hostname_nn']) \
        and (df['letter_nn'] == summary_dict['letter_nn']) \
        and (df['ProposalID'] == summary_dict['ProposalID'])]

    # Compare row against summary_dict, gather any differences and displace them later
    # Skip system, planet, star properties (sy_, pl_, st_)
    for key, value in summary_dict.items():
        if key.startswith('sy_') or key.startswith('pl_') or key.startswith('st_'):
            continue
        if row[key] != value:
            print(f"Difference found in {key}: {row[key]} != {value}")
    return


if __name__ == "__main__":
    df = read_data("data/03_trexolists_extended.csv")
    print(df.head())

    target_name = "WASP-96"
    planet_letter = "b"
    proposal_id = 2734
    summary_dict = gather_summary_info(proposal_id, target_name, planet_letter)

    # Compare the values
    compare_values(df, summary_dict)