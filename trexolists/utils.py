# Common utility scripts

import os


def normalize_text(text):
    """
    Normalize text content by treating "X" (case-insensitive) as None.
    
    Parameters
    ----------
    text : str or None
        Text value to normalize.
    
    Returns
    -------
    str or None
        Normalized text content, or None if input is None or "X".
    """
    if text is None:
        return None
    
    if isinstance(text, str):
        text = text.strip()
        # Treat "X" as equivalent to None (missing value)
        if text.upper() == "X":
            return None
        return text
    
    return text


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
        return normalize_text(found.text)
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
