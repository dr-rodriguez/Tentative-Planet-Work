# Script to parse the VSR xml file and save contents to a python dictionary

import xml.etree.ElementTree as ET
from trexolists.utils import safe_find_text, remove_all_whitespace


def parse_repeated_by(element):
    """
    Extract information from optional repeatedBy element.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        Visit XML element that may contain a repeatedBy child.

    Returns
    -------
    dict
        Dictionary with status, program, observation, visit, problemID.
        If repeatedBy element doesn't exist, status is "No" and others are None.
    """
    result = {
        "status": "No",
        "program": None,
        "observation": None,
        "visit": None,
        "problemID": None,
    }

    repeated_by = element.find("repeatedBy")
    if repeated_by is not None:
        result["status"] = "Yes"
        result["program"] = safe_find_text(repeated_by, "program")
        result["observation"] = safe_find_text(repeated_by, "observation")
        result["visit"] = safe_find_text(repeated_by, "visit")
        result["problemID"] = safe_find_text(repeated_by, "problemID")

    return result


def parse_repeat_of(element):
    """
    Extract information from optional repeatOf element.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        Visit XML element that may contain a repeatOf child.

    Returns
    -------
    dict
        Dictionary with status, program, observation, visit, problemID.
        If repeatOf element doesn't exist, status is "No" and others are None.
    """
    result = {
        "status": "No",
        "program": None,
        "observation": None,
        "visit": None,
        "problemID": None,
    }

    repeat_of = element.find("repeatOf")
    if repeat_of is not None:
        result["status"] = "Yes"
        result["program"] = safe_find_text(repeat_of, "program")
        result["observation"] = safe_find_text(repeat_of, "observation")
        result["visit"] = safe_find_text(repeat_of, "visit")
        result["problemID"] = safe_find_text(repeat_of, "problemID")

    return result


def parse_visits(root, target_name=None):
    """
    Parse all visit elements from VSR XML root.

    Parameters
    ----------
    root : xml.etree.ElementTree.Element
        Root element of the XML tree.
    target_name : str, optional
        Name of the target to get information for.

    Returns
    -------
    list of dict
        List of dictionaries containing visit information.
    """
    visits = []

    for visit_element in root.findall("visit"):
        visit_target = safe_find_text(visit_element, "target")

        # Skip visit if target_name is provided and does not match
        if target_name is not None:
            if visit_target is None or remove_all_whitespace(visit_target) != remove_all_whitespace(target_name):
                continue

        visit_dict = {
            "observation": visit_element.get("observation"),
            "visit": visit_element.get("visit"),
            "status": safe_find_text(visit_element, "status"),
            "target": visit_target,
            "configuration": safe_find_text(visit_element, "configuration"),
            "hours": safe_find_text(visit_element, "hours"),
            "longRangePlanStatus": safe_find_text(visit_element, "longRangePlanStatus"),
            "planWindow": safe_find_text(visit_element, "planWindow"),
            "startTime": safe_find_text(visit_element, "startTime"),
            "endTime": safe_find_text(visit_element, "endTime"),
            "repeatedBy": parse_repeated_by(visit_element),
            "repeatOf": parse_repeat_of(visit_element),
        }

        visits.append(visit_dict)

    return visits


def parse_vsr_file(file_path, target_name=None):
    """
    Parse a VSR XML file and extract visit status information.

    Parameters
    ----------
    file_path : str
        Path to the VSR XML file.
    target_name : str, optional
        Name of the target to get information for.

    Returns
    -------
    dict
        Dictionary containing VSR information fields. Missing fields are set to None.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Initialize all fields to None
    vsr_dict = {
        "observatory": None,
        "id": None,
        "title": None,
        "reportTime": None,
        "Visits": [],
    }

    # Extract root-level attributes
    vsr_dict["observatory"] = root.get("observatory")
    vsr_dict["id"] = root.get("id")

    # Extract root-level elements
    vsr_dict["title"] = safe_find_text(root, "title")
    vsr_dict["reportTime"] = safe_find_text(root, "reportTime")

    # Parse all visits
    vsr_dict["Visits"] = parse_visits(root, target_name=target_name)

    return vsr_dict


if __name__ == "__main__":
    # WASP-96 b
    file_path = "PPS/VSR/2734_VSR.xml"
    target_name = "WASP-96"

    # 55 Cnc e
    file_path = "PPS/VSR/2084_VSR.xml"
    target_name = "55 Cnc"

    vsr_dict = parse_vsr_file(file_path, target_name=target_name)

    # Pretty print the dictionary
    for key, value in vsr_dict.items():
        if key == "Visits":
            print(f"{key}: {len(value)} entries")
            for i, entry in enumerate(value, 1):
                print(f"  Entry {i}:")
                for sub_key, sub_value in entry.items():
                    print(f"    {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
