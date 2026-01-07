# Script to parse the APT xml file and save contents to a python dictionary

import xml.etree.ElementTree as ET
from trexolists.utils import safe_find_text

# XML namespace for JWST APT files
NS = "{http://www.stsci.edu/JWST/APT}"


def extract_text_by_tag(element, tag_pattern):
    """
    Extract text from a child element whose tag contains the given pattern.
    
    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        XML element to search within.
    tag_pattern : str
        String pattern to match in tag names.
    
    Returns
    -------
    str or None
        Text content of matching element, or None if not found.
    """
    for child in element:
        if tag_pattern in child.tag and child.text is not None:
            return child.text.strip()
    return None


def extract_common_attributes(templ):
    """
    Extract common attributes (Subarray, ReadoutPattern, Groups) from template element.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_subarray, obs_rop, obs_groups.
    """
    result = {
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None
    }
    
    for templ_attr in templ:
        if "Subarray" in templ_attr.tag:
            result["obs_subarray"] = templ_attr.text
        elif "ReadoutPattern" in templ_attr.tag:
            result["obs_rop"] = templ_attr.text
        elif "Groups" in templ_attr.tag:
            result["obs_groups"] = templ_attr.text
    
    return result


def extract_from_exposure(templ_attr):
    """
    Extract ReadoutPattern and Groups from nested Exposure element.
    
    Parameters
    ----------
    templ_attr : xml.etree.ElementTree.Element
        Exposure XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_rop and obs_groups.
    """
    result = {
        "obs_rop": None,
        "obs_groups": None
    }
    
    for exp_child in templ_attr:
        if "ReadoutPattern" in exp_child.tag:
            result["obs_rop"] = exp_child.text
        elif "Groups" in exp_child.tag:
            result["obs_groups"] = exp_child.text
    
    return result


def parse_niriss_soss(templ):
    """
    Parse NIRISS SOSS template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": "SOSS",
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    for templ_attr in templ:
        if "Subarray" in templ_attr.tag:
            result["obs_subarray"] = templ_attr.text
        elif "Exposure" in templ_attr.tag:
            exp_result = extract_from_exposure(templ_attr)
            result["obs_rop"] = exp_result["obs_rop"]
            result["obs_groups"] = exp_result["obs_groups"]
    
    return result


def parse_nircam_gts(templ):
    """
    Parse NIRCam Grism Time Series template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": "GTS",
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    common = extract_common_attributes(templ)
    result.update(common)
    
    for templ_attr in templ:
        if "LongPupilFilter" in templ_attr.tag:
            result["obs_opt_elem"] = templ_attr.text
    
    return result


def parse_nirspec_bots(templ):
    """
    Parse NIRSpec Bright Object Time Series template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": "BOTS",
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    common = extract_common_attributes(templ)
    result.update(common)
    
    for templ_attr in templ:
        if "Grating" in templ_attr.tag:
            result["obs_opt_elem"] = templ_attr.text
    
    return result


def parse_miri_lrs(templ):
    """
    Parse MIRI LRS template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": "LRS",
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    common = extract_common_attributes(templ)
    result.update(common)
    
    return result


def parse_miri_imaging(templ):
    """
    Parse MIRI Imaging template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": None,
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    for templ_attr in templ:
        if "Subarray" in templ_attr.tag:
            result["obs_subarray"] = templ_attr.text
        elif "Filters" in templ_attr.tag:
            for filter_config in templ_attr:
                if "FilterConfig" in filter_config.tag:
                    for fc_child in filter_config:
                        if "ReadoutPattern" in fc_child.tag:
                            result["obs_rop"] = fc_child.text
                        elif "Groups" in fc_child.tag:
                            result["obs_groups"] = fc_child.text
                        elif "Filter" in fc_child.tag:
                            result["obs_mode"] = fc_child.text
    
    return result


def parse_miri_mrs(templ):
    """
    Parse MIRI MRS template.
    
    Parameters
    ----------
    templ : xml.etree.ElementTree.Element
        Template XML element.
    
    Returns
    -------
    dict
        Dictionary with obs_mode, obs_subarray, obs_rop, obs_groups, obs_opt_elem.
    """
    result = {
        "obs_mode": None,
        "obs_subarray": None,
        "obs_rop": None,
        "obs_groups": None,
        "obs_opt_elem": None
    }
    
    for templ_attr in templ:
        if "Subarray" in templ_attr.tag:
            result["obs_subarray"] = templ_attr.text
        elif "Detector" in templ_attr.tag:
            result["obs_mode"] = templ_attr.text
        elif "ExposureList" in templ_attr.tag:
            for exp in templ_attr:
                if "Exposure" in exp.tag:
                    for exp_child in exp:
                        if "ReadoutPatternLong" in exp_child.tag:
                            result["obs_rop"] = exp_child.text
                        elif "GroupsLong" in exp_child.tag:
                            result["obs_groups"] = exp_child.text
    
    return result


# Template parser dispatch mapping
TEMPLATE_PARSERS = {
    "NirissSoss": parse_niriss_soss,
    "NircamGrismTimeSeries": parse_nircam_gts,
    "NirspecBrightObjectTimeSeries": parse_nirspec_bots,
    "MiriLRS": parse_miri_lrs,
    "MiriImaging": parse_miri_imaging,
    "MiriMRS": parse_miri_mrs,
}


def parse_targets(root, proposal_id, target_name=None):
    """
    Parse Targets section from APT XML.
    
    Parameters
    ----------
    root : xml.etree.ElementTree.Element
        Root element of the XML tree.
    proposal_id : str
        Proposal ID string.
    target_name : str, optional
        Name of the target to get information for.
    
    Returns
    -------
    list of dict
        List of dictionaries containing target information.
    """
    targets = []
    targets_node = root.find(f"{NS}Targets")
    
    if targets_node is None:
        return targets
    
    for target_element in targets_node.findall(f"{NS}Target"):
        # Skip target if target_name is provided and does not match
        if target_name is not None:
            if safe_find_text(target_element, f"{NS}TargetName") != target_name:
                continue
        
        target_dict = {
            "ProposalID": proposal_id,
            "Number": safe_find_text(target_element, f"{NS}Number"),
            "TargetName": safe_find_text(target_element, f"{NS}TargetName"),
            "TargetArchiveName": safe_find_text(target_element, f"{NS}TargetArchiveName"),
            "TargetID": safe_find_text(target_element, f"{NS}TargetID"),
            "Comments": safe_find_text(target_element, f"{NS}Comments"),
            "RAProperMotion": safe_find_text(target_element, f"{NS}RAProperMotion"),
            "DecProperMotion": safe_find_text(target_element, f"{NS}DecProperMotion"),
            "RAProperMotionUnits": safe_find_text(target_element, f"{NS}RAProperMotionUnits"),
            "DecProperMotionUnits": safe_find_text(target_element, f"{NS}DecProperMotionUnits"),
            "Epoch": safe_find_text(target_element, f"{NS}Epoch"),
            "AnnualParallax": safe_find_text(target_element, f"{NS}AnnualParallax"),
            "Extended": safe_find_text(target_element, f"{NS}Extended"),
            "Category": safe_find_text(target_element, f"{NS}Category"),
            "Keywords": safe_find_text(target_element, f"{NS}Keywords"),
            "EquatorialCoordinates": None,
            "BackgroundTargetReq": safe_find_text(target_element, f"{NS}BackgroundTargetReq"),
            "TargetConfirmationRun": safe_find_text(target_element, f"{NS}TargetConfirmationRun")
        }
        
        # Extract EquatorialCoordinates Value attribute
        eq_coords = target_element.find(f"{NS}EquatorialCoordinates")
        if eq_coords is not None:
            target_dict["EquatorialCoordinates"] = eq_coords.get("Value")
        
        targets.append(target_dict)
    
    return targets


def parse_data_requests(root, proposal_id, target_name=None):
    """
    Parse DataRequests section from APT XML.
    
    Parameters
    ----------
    root : xml.etree.ElementTree.Element
        Root element of the XML tree.
    proposal_id : str
        Proposal ID string.
    target_name : str, optional
        Name of the target to get information for.
    
    Returns
    -------
    list of dict
        List of dictionaries containing observation information.
    """
    observations = []
    data_requests_node = root.find(f"{NS}DataRequests")
    
    if data_requests_node is None:
        return observations
    
    for obs_group in data_requests_node.findall(f"{NS}ObservationGroup"):
        dr_label = safe_find_text(obs_group, f"{NS}Label")
        if dr_label is None:
            dr_label = "NONE"
        
        for observation in obs_group.findall(f"{NS}Observation"):
            obs_number = safe_find_text(observation, f"{NS}Number")
            obs_target = safe_find_text(observation, f"{NS}TargetID")
            obs_label2 = safe_find_text(observation, f"{NS}Label")
            obs_instrument = safe_find_text(observation, f"{NS}Instrument")
            
            # Parse TargetID to extract target number
            obs_target_id = None
            if obs_target:
                ws_idx = obs_target.find(' ')
                if ws_idx >= 1:
                    obs_target_id = obs_target[0:ws_idx]
                    obs_target = obs_target[ws_idx:].strip()

            # Skip observation if target_name is provided and does not match
            if target_name is not None:
                if obs_target.strip() != target_name.strip():
                    continue
            
            # Initialize observation mode and template-specific fields
            obs_mode = None
            obs_subarray = None
            obs_rop = None
            obs_groups = None
            obs_opt_elem = None
            
            # Parse Template to extract observing mode and parameters
            template = observation.find(f"{NS}Template")
            if template is not None:
                for templ in template:
                    templ_tag = templ.tag
                    
                    # Find matching parser function
                    parser_func = None
                    for template_key, parser in TEMPLATE_PARSERS.items():
                        if template_key in templ_tag:
                            parser_func = parser
                            break
                    
                    # Parse template if a matching parser was found
                    if parser_func is not None:
                        result = parser_func(templ)
                        obs_mode = result["obs_mode"]
                        obs_subarray = result["obs_subarray"]
                        obs_rop = result["obs_rop"]
                        obs_groups = result["obs_groups"]
                        obs_opt_elem = result["obs_opt_elem"]
            
            # Extract ScienceDuration and CoordinatedParallel
            obs_sci_dur = safe_find_text(observation, f"{NS}ScienceDuration")
            obs_coord_par = safe_find_text(observation, f"{NS}CoordinatedParallel")
            
            # Parse SpecialRequirements
            obs_zero_phase = None
            obs_period = None
            obs_phase_start = None
            obs_phase_end = None
            obs_tso = None
            
            special_req = observation.find(f"{NS}SpecialRequirements")
            if special_req is not None:
                period_zero_phase = special_req.find(f"{NS}PeriodZeroPhase")
                if period_zero_phase is not None:
                    obs_zero_phase = period_zero_phase.get("ZeroPhase")
                    obs_period = period_zero_phase.get("Period")
                    obs_phase_start = period_zero_phase.get("PhaseStart")
                    obs_phase_end = period_zero_phase.get("PhaseEnd")
                
                if special_req.find(f"{NS}TimeSeriesObservation") is not None:
                    obs_tso = 1
            
            obs_dict = {
                "ProposalID": proposal_id,
                "Label": dr_label,
                "Obs_Number": obs_number,
                "TargetID": obs_target,
                "Target_Number": obs_target_id,
                "Label2": obs_label2,
                "Instrument": obs_instrument,
                "ObservingMode": obs_mode,
                "ScienceDuration": obs_sci_dur,
                "CoordinatedParallel": obs_coord_par,
                "ZeroPhase": obs_zero_phase,
                "Period": obs_period,
                "PhaseStart": obs_phase_start,
                "PhaseEnd": obs_phase_end,
                "TimeSeriesObservation": obs_tso,
                "Subarray": obs_subarray,
                "ReadoutPattern": obs_rop,
                "Groups": obs_groups,
                "GratingGrism": obs_opt_elem
            }
            
            observations.append(obs_dict)
    
    return observations


def parse_apt_file(file_path, target_name=None):
    """
    Parse an APT XML file and extract proposal information.
    
    Parameters
    ----------
    file_path : str
        Path to the APT XML file.
    target_name : str, optional
        Name of the target to get information for.

    Returns
    -------
    dict
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
        "LastName": None,
        "Targets": [],
        "DataRequests": []
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
    
    # Parse Targets section
    proposal_id = apt_dict["ProposalID"]
    if proposal_id:
        apt_dict["Targets"] = parse_targets(root, proposal_id, target_name=target_name)
        apt_dict["DataRequests"] = parse_data_requests(root, proposal_id, target_name=target_name)
    
    return apt_dict


if __name__ == "__main__":
    file_path = "PPS/APT/2734_APT.xml"
    target_name = "WASP-96"  # optional target name, need to strip component letter if present
    apt_dict = parse_apt_file(file_path, target_name=target_name)

    # Pretty print the dictionary
    for key, value in apt_dict.items():
        if key in ["Targets", "DataRequests"]:
            print(f"{key}: {len(value)} entries")
            for i, entry in enumerate(value, 1):
                print(f"  Entry {i}:")
                for sub_key, sub_value in entry.items():
                    print(f"    {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
