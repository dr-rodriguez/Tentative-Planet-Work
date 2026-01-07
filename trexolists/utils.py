# Common utility scripts

import os


def safe_find_text(element, tag):
    """
    Safely find and return text content of an element, or None if not found.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        XML element to search within.
    tag : str
        Tag name to search for.

    Returns
    -------
    str or None
        Text content of the element, or None if not found.
    """
    found = element.find(tag)
    if found is not None and found.text is not None:
        text = found.text.strip()
        # Treat "X" as equivalent to None (missing value)
        if text.upper() == "X":
            return None
        return text
    return None


def check_directory(directory):
    """
    Create directory if it does not exist.

    Parameters
    ----------
    directory : str
        Path to the directory to create.
    """
    os.makedirs(directory, exist_ok=True)
