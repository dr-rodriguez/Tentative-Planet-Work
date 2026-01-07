# Read the data from the csv file and compare against APT/VSR information

import pandas as pd
from trexolists.get_summary import gather_summary_info


def read_data(file_path):
    df = pd.read_csv(file_path)
    return df


def normalize_value(value):
    """
    Normalize a value to a standard type for comparison.
    Returns a tuple of (normalized_value, type_category) where type_category is 'numeric', 'string', or 'none'.
    """
    # Handle None/NaN
    if value is None or pd.isna(value):
        return None, "none"

    # Try to convert to numeric (int or float)
    if isinstance(value, (int, float)):
        # Convert int to float for consistent numeric comparison
        return float(value), "numeric"

    if isinstance(value, str):
        # Try to convert string to numeric
        value_stripped = value.strip()
        # Only treat empty strings as None, preserve "X" and other values
        if not value_stripped or value_stripped.upper() in ["NONE", "NULL", "X"]:
            return None, "none"

        # Try int first, then float
        try:
            # Check if it's an integer (no decimal point)
            if "." not in value_stripped and "e" not in value_stripped.lower():
                return int(value_stripped), "numeric"
            else:
                return float(value_stripped), "numeric"
        except (ValueError, TypeError):
            # Not numeric, return as string
            return str(value), "string"

    # For other types, convert to string
    return str(value), "string"


def compare_values(df, summary_dict):
    # Get the corresponding row in the dataframe
    # Convert ProposalID to same type for comparison (handle int/string mismatch)
    proposal_id = summary_dict["ProposalID"]
    if proposal_id is not None:
        # Try to convert to int if it's a string
        if isinstance(proposal_id, str):
            try:
                proposal_id = int(proposal_id)
            except (ValueError, TypeError):
                pass

    mask = (
        (df["hostname_nn"] == summary_dict["hostname_nn"])
        & (df["letter_nn"] == summary_dict["letter_nn"])
        & (df["ProposalID"] == proposal_id)
    )

    matching_rows = df[mask]

    if matching_rows.empty:
        print(
            f"No matching row found for hostname={summary_dict['hostname_nn']}, "
            f"letter={summary_dict['letter_nn']}, ProposalID={summary_dict['ProposalID']}"
        )
        return

    # Normalize summary_dict Observation for comparison
    summary_obs_norm, summary_obs_type = normalize_value(summary_dict.get("Observation"))

    # Loop over each matching row
    for idx, row in matching_rows.iterrows():
        # Extract row as dictionary
        row_dict = row.to_dict()
        
        # Print the Observation value for this row
        row_observation = row_dict.get("Observation")
        print(f"Processing Observation: {row_observation}")

        # Normalize row Observation for comparison
        row_obs_norm, row_obs_type = normalize_value(row_observation)

        # Check if Observation fields match
        observation_matches = False
        if summary_obs_type == "none" and row_obs_type == "none":
            observation_matches = True
        elif summary_obs_type == "numeric" and row_obs_type == "numeric":
            observation_matches = abs(summary_obs_norm - row_obs_norm) < 1e-9
        elif summary_obs_type == "string" and row_obs_type == "string":
            observation_matches = summary_obs_norm == row_obs_norm

        if not observation_matches:
            print(
                f"Skipping row with Observation={row_observation} "
                f"(does not match summary_dict Observation={summary_dict.get('Observation')})"
            )
            continue

        # Compare row against summary_dict, gather any differences and display them
        # Skip system, planet, star properties (sy_, pl_, st_)
        for key, value in summary_dict.items():
            if key.startswith("sy_") or key.startswith("pl_") or key.startswith("st_"):
                continue

            # Skip if key doesn't exist in row_dict
            if key not in row_dict:
                print(f"Key '{key}' not found in dataframe row")
                continue

            row_value = row_dict[key]

            # Normalize both values
            row_norm, row_type = normalize_value(row_value)
            val_norm, val_type = normalize_value(value)

            # Handle None/NaN values
            if row_type == "none" and val_type == "none":
                continue  # Both are None/NaN, consider them equal
            elif row_type == "none" or val_type == "none":
                print(f"Difference found in {key}: {row_value} != {value}")
                continue

            # Compare normalized values
            if row_type == "numeric" and val_type == "numeric":
                # Numeric comparison with small tolerance for floating point
                if abs(row_norm - val_norm) > 1e-9:
                    print(f"Difference found in {key}: {row_value} != {value}")
            elif row_type == "string" and val_type == "string":
                # String comparison
                if row_norm != val_norm:
                    print(f"Difference found in {key}: {row_value} != {value}")
            else:
                # Type mismatch (numeric vs string) - these are likely real differences
                print(
                    f"Difference found in {key}: {row_value} != {value} (type mismatch: {row_type} vs {val_type})"
                )
    return


if __name__ == "__main__":
    df = read_data("data/03_trexolists_extended.csv")
    # print(df.head())

    # WASP-96 b
    # target_name = "WASP-96"
    # planet_letter = "b"
    # proposal_id = 2734

    # K2-34 b
    # target_name = "K2-34"
    # planet_letter = "b"
    # proposal_id = 1541

    # 55 Cnc e
    target_name = "55 Cnc"
    planet_letter = "e"
    proposal_id = 2084

    summary_dict = gather_summary_info(proposal_id, target_name, planet_letter)

    # Compare the values
    compare_values(df, summary_dict)
