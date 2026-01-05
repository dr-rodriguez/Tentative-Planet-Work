# Script to parse the APT xml file and save contents to a python dictionary

import xml.etree.ElementTree as ET

# XML namespace for JWST APT files
NS = "{http://www.stsci.edu/JWST/APT}"


def safe_find_text(element, tag):
    """Safely find and return text content of an element, or None if not found."""
    found = element.find(tag)
    if found is not None and found.text is not None:
        return found.text.strip()
    return None


def parse_apt_file(file_path):
    """
    Parse an APT XML file and extract proposal information.
    
    Args:
        file_path: Path to the APT XML file
        
    Returns:
        Dictionary containing proposal information fields. Missing fields are set to None.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Initialize all fields to None
    apt_dict = {
        "ProposalPhase": None,
        "Title": None,
        "Abstract": None,
        "ProposalID": None,
        "StsciEditNumber": None,
        "ProposalCategory": None,
        "ProposalSize": None,
        "ProprietaryPeriod": None,
        "Cycle": None,
        "AllocatedTime": None,
        "ChargedTime": None,
        "ObservingDescription": None,
        "LastName": None
    }
    
    # Find ProposalInformation node
    proposal_info = root.find(f"{NS}ProposalInformation")
    if proposal_info is None:
        return apt_dict
    
    # Extract simple fields directly from ProposalInformation
    apt_dict["ProposalPhase"] = safe_find_text(proposal_info, f"{NS}ProposalPhase")
    apt_dict["Title"] = safe_find_text(proposal_info, f"{NS}Title")
    apt_dict["Abstract"] = safe_find_text(proposal_info, f"{NS}Abstract")
    apt_dict["ProposalID"] = safe_find_text(proposal_info, f"{NS}ProposalID")
    apt_dict["StsciEditNumber"] = safe_find_text(proposal_info, f"{NS}StsciEditNumber")
    apt_dict["ProposalCategory"] = safe_find_text(proposal_info, f"{NS}ProposalCategory")
    apt_dict["ProposalSize"] = safe_find_text(proposal_info, f"{NS}ProposalSize")
    apt_dict["ProprietaryPeriod"] = safe_find_text(proposal_info, f"{NS}ProprietaryPeriod")
    apt_dict["Cycle"] = safe_find_text(proposal_info, f"{NS}Cycle")
    apt_dict["AllocatedTime"] = safe_find_text(proposal_info, f"{NS}AllocatedTime")
    apt_dict["ChargedTime"] = safe_find_text(proposal_info, f"{NS}ChargedTime")
    apt_dict["ObservingDescription"] = safe_find_text(proposal_info, f"{NS}ObservingDescription")
    
    # Extract LastName from nested PrincipalInvestigator structure
    principal_investigator = proposal_info.find(f"{NS}PrincipalInvestigator")
    if principal_investigator is not None:
        investigator_address = principal_investigator.find(f"{NS}InvestigatorAddress")
        if investigator_address is not None:
            apt_dict["LastName"] = safe_find_text(investigator_address, f"{NS}LastName")
    
    return apt_dict

if __name__ == "__main__":
    file_path = "PPS/APT/2734_APT.xml"
    apt_dict = parse_apt_file(file_path)
    for key, value in apt_dict.items():
        print(f"{key}: {value}")
