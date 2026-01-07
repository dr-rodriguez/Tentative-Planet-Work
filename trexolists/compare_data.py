# Read the data from the csv file and compare against APT/VSR information

import pandas as pd
from trexolists.get_summary import gather_summary_info


def read_data(file_path):
    df = pd.read_csv(file_path)
    return df


def compare_values(df, summary_dict):
    # Get the corresponding row in the dataframe
    # Convert ProposalID to same type for comparison (handle int/string mismatch)
    proposal_id = summary_dict['ProposalID']
    if proposal_id is not None:
        # Try to convert to int if it's a string
        if isinstance(proposal_id, str):
            try:
                proposal_id = int(proposal_id)
            except (ValueError, TypeError):
                pass
    
    mask = ((df['hostname_nn'] == summary_dict['hostname_nn']) &
            (df['letter_nn'] == summary_dict['letter_nn']) &
            (df['ProposalID'] == proposal_id))
    
    matching_rows = df[mask]
    
    if matching_rows.empty:
        print(f"No matching row found for hostname={summary_dict['hostname_nn']}, "
              f"letter={summary_dict['letter_nn']}, ProposalID={summary_dict['ProposalID']}")
        return
    
    # Extract first matching row and convert to dictionary
    row_dict = matching_rows.iloc[0].to_dict()

    # Compare row against summary_dict, gather any differences and display them
    # Skip system, planet, star properties (sy_, pl_, st_)
    for key, value in summary_dict.items():
        if key.startswith('sy_') or key.startswith('pl_') or key.startswith('st_'):
            continue
        
        # Skip if key doesn't exist in row_dict
        if key not in row_dict:
            print(f"Key '{key}' not found in dataframe row")
            continue
        
        row_value = row_dict[key]
        
        # Handle NaN/None values properly
        if pd.isna(row_value) and (value is None or pd.isna(value)):
            continue  # Both are NaN/None, consider them equal
        elif pd.isna(row_value) or (value is None or pd.isna(value)):
            print(f"Difference found in {key}: {row_value} != {value}")
            continue
        
        # Compare values (handle type mismatches)
        try:
            if row_value != value:
                print(f"Difference found in {key}: {row_value} != {value}")
        except (TypeError, ValueError) as e:
            print(f"Error comparing {key}: {e} (row_value={row_value}, value={value})")
    return


if __name__ == "__main__":
    df = read_data("data/03_trexolists_extended.csv")
    # print(df.head())

    target_name = "WASP-96"
    planet_letter = "b"
    proposal_id = 2734
    summary_dict = gather_summary_info(proposal_id, target_name, planet_letter)

    # Compare the values
    compare_values(df, summary_dict)