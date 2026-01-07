# Script to get the Trexolist summary information for a given planet/proposal ID

import os
from astropy.time import Time
from trexolists.parse_apt import parse_apt_file
from trexolists.parse_vsr import parse_vsr_file
from trexolists.pps_fetch import download_apt, download_vsr, check_apt_file, check_vsr_file

# Defaults
work_dir = "."
apt_dir = os.path.join(work_dir, "PPS", "APT")
vsr_dir = os.path.join(work_dir, "PPS", "VSR")


def parse_vsr_date(date_string):
    """
    Parse VSR date format and convert to decimal year and formatted string.
    
    Parameters
    ----------
    date_string : str
        Date string in format "Jun 21, 2022 02:41:18"
    
    Returns
    -------
    tuple
        (decimal_year, formatted_string) where decimal_year is float and formatted_string is "YYYY-MM-DD--HH:MM:SS"
        Returns (None, None) if parsing fails
    """
    if not date_string:
        return None, None
    
    try:
        # Parse month name to number
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        # Format: "Jun 21, 2022 02:41:18"
        parts = date_string.split(',')
        if len(parts) < 2:
            return None, None
        
        month_day = parts[0].strip()
        month_day_parts = month_day.split()
        if len(month_day_parts) < 2:
            return None, None
        month = month_day_parts[0]
        day = month_day_parts[1]
        
        year_time = parts[1].strip()
        year_time_parts = year_time.split()
        if len(year_time_parts) < 2:
            return None, None
        year = year_time_parts[0]
        time = year_time_parts[1]
        
        if not all([month, day, year, time]):
            return None, None
        
        month_num = month_map.get(month)
        if not month_num:
            return None, None
        
        # Format day with leading zero if needed
        day = day.zfill(2)
        
        # Create ISO format string: "2022-06-21T02:41:18"
        iso_string = f"{year}-{month_num}-{day}T{time}"
        
        # Calculate decimal year
        decimal_year = round(Time(iso_string, format='isot').decimalyear, 3)
        
        # Create formatted string: "2022-06-21--02:41:18"
        formatted_string = f"{year}-{month_num}-{day}--{time}"
        
        return decimal_year, formatted_string
    except Exception:
        return None, None


def summary_info(apt_dict, target_name, planet_letter, vsr_dict=None):
    """
    Extract summary information matching CSV column structure from data/03_trexolists_extended.csv.
    
    Returns a dictionary with keys matching CSV column names:
    hostname_nn, letter_nn, Event, ProposalCategory, ProposalID, Cycle, Observation, Status,
    ObservingMode, GratingGrism, Subarray, ReadoutPattern, Groups, StartTime, EndTime, Hours,
    LastName, ProprietaryPeriod, EquatorialCoordinates, sy_kmag, sy_dist, st_teff, st_mass,
    st_rad, st_logg, pl_orbper, pl_orbsmax, pl_orbincl, pl_massj, pl_radj, pl_g_SI, pl_dens_cgs,
    pl_Teq_K, pl_trandep, pl_trandur, pl_TSM_K, pl_ESM_3um, PlanWindow, st_met
    """

    result = {
        "hostname_nn": target_name,
        "letter_nn": planet_letter,
        "Event": None,
        "ProposalCategory": None,
        "ProposalID": None,
        "Cycle": None,
        "Observation": None,
        "Status": None,
        "ObservingMode": None,
        "GratingGrism": None,
        "Subarray": None,
        "ReadoutPattern": None,
        "Groups": None,
        "StartTime": None,
        "EndTime": None,
        "Hours": None,
        "LastName": None,
        "ProprietaryPeriod": None,
        "EquatorialCoordinates": None,
        "sy_kmag": None,
        "sy_dist": None,
        "st_teff": None,
        "st_mass": None,
        "st_rad": None,
        "st_logg": None,
        "pl_orbper": None,
        "pl_orbsmax": None,
        "pl_orbincl": None,
        "pl_massj": None,
        "pl_radj": None,
        "pl_g_SI": None,
        "pl_dens_cgs": None,
        "pl_Teq_K": None,
        "pl_trandep": None,
        "pl_trandur": None,
        "pl_TSM_K": None,
        "pl_ESM_3um": None,
        "PlanWindow": None,
        "st_met": None,
    }

    # Extract top-level fields
    result["ProposalID"] = apt_dict.get("ProposalID")
    result["ProposalCategory"] = apt_dict.get("ProposalCategory")
    result["Cycle"] = apt_dict.get("Cycle")
    result["LastName"] = apt_dict.get("LastName")
    result["ProprietaryPeriod"] = apt_dict.get("ProprietaryPeriod")

    # Find matching observations from DataRequests
    data_requests = apt_dict.get("DataRequests", [])
    matching_obs = [obs for obs in data_requests if obs.get("TargetID") == target_name]
    
    if matching_obs:
        # Use first matching observation
        obs = matching_obs[0]
        result["Observation"] = obs.get("Obs_Number")
        
        # Format observing mode: Instrument + " " + ObservingMode
        instrument = obs.get("Instrument")
        obs_mode = obs.get("ObservingMode")
        if instrument and obs_mode:
            result["ObservingMode"] = f"{instrument} {obs_mode}"
        elif instrument:
            result["ObservingMode"] = instrument
        elif obs_mode:
            result["ObservingMode"] = obs_mode
        
        result["Subarray"] = obs.get("Subarray")
        result["ReadoutPattern"] = obs.get("ReadoutPattern")
        result["Groups"] = obs.get("Groups")
        result["GratingGrism"] = obs.get("GratingGrism")
        
        # Determine Event field - set to "Transit" if TimeSeriesObservation is detected
        # if obs.get("TimeSeriesObservation") == 1:
        #     result["Event"] = "Transit"
        
        # Match VSR visit to this observation
        if vsr_dict:
            visits = vsr_dict.get("Visits", [])
            obs_number = obs.get("Obs_Number")
            if obs_number:
                # Find matching visit by observation number
                matching_visit = None
                for visit in visits:
                    if visit.get("observation") == str(obs_number):
                        matching_visit = visit
                        break
                
                if matching_visit:
                    # Extract Status
                    result["Status"] = matching_visit.get("status")
                    
                    # Extract Hours (convert to float if present)
                    hours_str = matching_visit.get("hours")
                    if hours_str:
                        try:
                            result["Hours"] = float(hours_str)
                        except (ValueError, TypeError):
                            result["Hours"] = None
                    
                    # Extract StartTime and EndTime in raw format
                    result["StartTime"] = matching_visit.get("startTime")
                    result["EndTime"] = matching_visit.get("endTime")
                    
                    # Extract PlanWindow (use "X" if None or empty)
                    plan_window = matching_visit.get("planWindow")
                    if plan_window:
                        result["PlanWindow"] = plan_window
                    else:
                        result["PlanWindow"] = "X"

    # Find matching target from Targets list
    targets = apt_dict.get("Targets", [])
    matching_target = None
    for target in targets:
        if target.get("TargetName") == target_name:
            matching_target = target
            break
    
    # Extract EquatorialCoordinates in raw format
    if matching_target:
        result["EquatorialCoordinates"] = matching_target.get("EquatorialCoordinates")

    return result


if __name__ == "__main__":
    proposal_id = 2734
    target_name = "WASP-96"
    planet_letter = "b"

    # Check if the APT and VSR files exist
    if not check_apt_file(proposal_id):
        download_apt(proposal_id)
    if not check_vsr_file(proposal_id):
        download_vsr(proposal_id)

    apt_file = os.path.join(apt_dir, f"{proposal_id}_APT.xml")
    vsr_file = os.path.join(vsr_dir, f"{proposal_id}_VSR.xml")
    apt_dict = parse_apt_file(apt_file, target_name)
    vsr_dict = parse_vsr_file(vsr_file, target_name)

    summary_info = summary_info(apt_dict, target_name, planet_letter, vsr_dict)

    for key, value in summary_info.items():
        print(f"{key}: {value}")