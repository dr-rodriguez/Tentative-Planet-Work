# Script to get the Trexolist summary information for a given planet/proposal ID

import os
from parse_apt import parse_apt_file
from pps_fetch import download_apt, download_vsr, check_apt_file, check_vsr_file

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
    }

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

    print(apt_dict)