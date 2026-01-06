# Script to get the Trexolist summary information for a given planet/proposal ID

import os
from trexolists.parse_apt import parse_apt_file
from trexolists.pps_fetch import download_apt, download_vsr, check_apt_file, check_vsr_file

# Defaults
work_dir = "."
apt_dir = os.path.join(work_dir, "PPS", "APT")
vsr_dir = os.path.join(work_dir, "PPS", "VSR")

def summary_info(apt_dict, target_name, planet_letter):
    """

    HTML columns that are being used:
    <th>Star<br>name</th>
    <th>Planet<br>letter</th>
    <th>Event</th>
    <th>Program</th>
    <th>Cycle</th>
    <th>Obs.</th>
    <th>Visit status<sup>*</sup></th>
    <th>Observing Mode</th>
    <th>Subarray</th>
    <th>Readout<br>pattern</th>
    <th>Groups</th>
    <th>Start UT<br>decimal</th>
    <th>Start UT<br>YYYY-mm-dd--<br>hh:mm:ss</th>
    <th>Hours</th>
    <th>PI name</th>
    <th>Propr.<br>Period,<br>mo</th>
    <th>RA (2000)<br>hh:mm:ss</th>
    <th>Dec (2000)<br>dd:mm:ss</th>
    <th>Star<br>K<sub>mag</sub></th>
    <th>d<sub>star</sub>,<br>parsec</th>
    <th>Star<br>T<sub>eff</sub>,<br>K</th>
    <th>Star<br>[Fe/H]</th>
    <th>Star<br>logg,<br>cgs</th>
    <th>Star<br>mass,<br>M<sub>Sun</sub></th>
    <th>Star<br>radius,<br>R<sub>Sun</sub></th>
    <th>Orbital<br>period,<br>day</th>
    <th>Semi-<br>m. axis,<br>AU</th>
    <th>Orbital<br>inclin.,<br>degree</th>
    <th>Planet<br>mass,<br>M<sub>Jup</sub></th>
    <th>Planet<br>radius,<br>R<sub>Jup</sub></th>
    <th>Planet<br>gravity,</br>m/s<sup>2</sup></th>
    <th>Planet<br>density,<br>g/cm<sup>3</sup></th>
    <th>Planet<br>eq. temp.,<br>K</th>
    <th>Transit<br>depth,<br>percent</th>
    <th>Transit<br>duration,<br>hr</th>
    <th>Planet<br>TSM<br> at 3 um</th>
    <th>Planet<br>ESM<br> at 3 um</th>
    <th>Plan window<sup>*</sup></th>

    Values for WASP-96 b:
    <tr><td>WASP-96</td><td>b</td><td>Transit</td><td><a href="https://www.stsci.edu/jwst-program-info/download/jwst/pdf/2734/">COM 2734</a></td><td>0</td><td>2</td><td>Archived</td><td>NIRISS SOSS</td><td>SUBSTRIP256</td><td>NISRAPID</td><td>14.0</td><td>2022.469</td><td>2022-06-21--02:41:18</td><td>7.51</td><td>Pontoppidan</td><td>12</td><td>00:04:11.1377</td><td>-47:21:38.32</td><td>10.914</td><td>352.46</td><td>5540.0</td><td>0.14</td><td>4.42</td><td>1.06</td><td>1.05</td><td>3.4252567</td><td>0.045</td><td>85.6</td><td>0.48</td><td>1.23</td><td>8.99</td><td>0.39</td><td>1285.4</td><td>1.4</td><td>2.4</td><td>123.64</td><td>17.11</td><td>X</td></tr>
    """

    result = {
        "StarName": target_name,
        "PlanetLetter": planet_letter,
        "Event": None,
        "Program": None,
        "Cycle": None,
        "Obs": None,
        "VisitStatus": None,
        "ObservingMode": None,
        "Subarray": None,
        "ReadoutPattern": None,
        "Groups": None,
        "StartUTDecimal": None,
        "StartUTFormatted": None,
        "Hours": None,
        "PIName": None,
        "ProprietaryPeriod": None,
        "RA": None,
        "Dec": None,
        "StarKmag": None,
        "StarDistance": None,
        "StarTeff": None,
        "StarFeH": None,
        "Starlogg": None,
        "StarMass": None,
        "StarRadius": None,
        "OrbitalPeriod": None,
        "SemiMajorAxis": None,
        "OrbitalInclination": None,
        "PlanetMass": None,
        "PlanetRadius": None,
        "PlanetGravity": None,
        "PlanetDensity": None,
        "PlanetEqTemp": None,
        "TransitDepth": None,
        "TransitDuration": None,
        "PlanetTSM": None,
        "PlanetESM": None,
        "PlanWindow": None,
    }

    # Extract top-level fields
    if apt_dict.get("ProposalID"):
        # TODO: Figure out how COM is set and what other values are possible
        # result["Program"] = f"COM {apt_dict['ProposalID']}"
        result["Program"] = apt_dict['ProposalID']

    result["Cycle"] = apt_dict.get("Cycle")
    result["PIName"] = apt_dict.get("LastName")
    result["ProprietaryPeriod"] = apt_dict.get("ProprietaryPeriod")

    # Find matching observations from DataRequests
    data_requests = apt_dict.get("DataRequests", [])
    matching_obs = [obs for obs in data_requests if obs.get("TargetID") == target_name]
    
    if matching_obs:
        # Use first matching observation
        obs = matching_obs[0]
        result["Obs"] = obs.get("Obs_Number")
        
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

    # Find matching target from Targets list
    targets = apt_dict.get("Targets", [])
    matching_target = None
    for target in targets:
        if target.get("TargetName") == target_name:
            matching_target = target
            break
    
    # NOTE: This would be replaced in the final version with info from nexsci
    if matching_target:
        # Parse EquatorialCoordinates Value attribute
        # Format: "00 04 11.1377 -47 21 38.32" -> RA: "00:04:11.1377", Dec: "-47:21:38.32"
        eq_coords = matching_target.get("EquatorialCoordinates")
        if eq_coords:
            parts = eq_coords.split()
            if len(parts) >= 6:
                ra_hh = parts[0]
                ra_mm = parts[1]
                ra_ss = parts[2]
                dec_dd = parts[3]
                dec_mm = parts[4]
                dec_ss = parts[5]
                
                result["RA"] = f"{ra_hh}:{ra_mm}:{ra_ss}"
                result["Dec"] = f"{dec_dd}:{dec_mm}:{dec_ss}"

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

    summary_info = summary_info(apt_dict, target_name, planet_letter)

    for key, value in summary_info.items():
        print(f"{key}: {value}")