# TrExoLiSTS

## Module Documentation

This document describes the Python modules in the `trexolists` directory and their functions.

### compare_data.py

Data comparison utilities for comparing CSV data against APT/VSR information.

- `read_data(file_path)` - Reads CSV data from a file path
- `normalize_value(value)` - Normalizes a value to a standard type for comparison (numeric, string, or none)
- `compare_values(df, summary_dict)` - Compares dataframe values against summary dictionary and displays differences

### get_summary.py

Summary information extraction from APT and VSR files.

- `parse_vsr_date(date_string)` - Parses VSR date format and converts to decimal year and formatted string
- `summary_info(apt_dict, target_name, planet_letter, vsr_dict=None)` - Extracts summary information matching CSV column structure from APT/VSR data
- `gather_summary_info(proposal_id, target_name, planet_letter)` - Gathers summary information for a given proposal ID, target name, and planet letter

### parse_apt.py

APT XML file parsing utilities for extracting proposal information.

- `is_groups_tag(tag)` - Checks if a tag is exactly 'Groups' (not 'AcqGroups' or 'VerificationGroups')
- `extract_text_by_tag(element, tag_pattern)` - Extracts text from a child element whose tag contains the given pattern
- `extract_common_attributes(templ)` - Extracts common attributes (Subarray, ReadoutPattern, Groups) from template element
- `extract_from_exposure(templ_attr)` - Extracts ReadoutPattern and Groups from nested Exposure element
- `parse_niriss_soss(templ)` - Parses NIRISS SOSS template
- `parse_nircam_gts(templ)` - Parses NIRCam Grism Time Series template
- `parse_nirspec_bots(templ)` - Parses NIRSpec Bright Object Time Series template
- `parse_miri_lrs(templ)` - Parses MIRI LRS template
- `parse_miri_imaging(templ)` - Parses MIRI Imaging template
- `parse_miri_mrs(templ)` - Parses MIRI MRS template
- `parse_targets(root, proposal_id, target_name=None)` - Parses Targets section from APT XML
- `parse_data_requests(root, proposal_id, target_name=None)` - Parses DataRequests section from APT XML
- `parse_apt_file(file_path, target_name=None)` - Parses an APT XML file and extracts proposal information

### parse_vsr.py

VSR XML file parsing utilities for extracting visit status information.

- `parse_repeated_by(element)` - Extracts information from optional repeatedBy element
- `parse_repeat_of(element)` - Extracts information from optional repeatOf element
- `parse_visits(root, target_name=None)` - Parses all visit elements from VSR XML root
- `parse_vsr_file(file_path, target_name=None)` - Parses a VSR XML file and extracts visit status information

### pps_fetch.py

PPS data fetching utilities for downloading APT and VSR files.

- `check_apt_file(program_id)` - Checks if APT file exists for the given program ID
- `download_apt(program_id)` - Downloads and extracts APT file for the given program ID
- `download_vsr(program_id)` - Downloads VSR file for the given program ID
- `check_vsr_file(program_id)` - Checks if VSR file exists for the given program ID
- `main()` - Loops over program IDs and fetches APT and VSR files

### utils.py

Common utility functions used across the project.

- `normalize_text(text)` - Normalizes text content by treating "X" (case-insensitive) as None
- `safe_find_text(element, tag)` - Safely finds and returns text content of an XML element, or None if not found
- `remove_all_whitespace(text)` - Removes all whitespace characters from a string and converts to uppercase
- `check_directory(directory)` - Creates directory if it does not exist
