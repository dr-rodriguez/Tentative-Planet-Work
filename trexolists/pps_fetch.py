# Script to fetch the JWST PPS data (APT and VSR files)

import os
import requests
import shutil
from trexolists.utils import check_directory

# Define the base URL for the PPS data
base_url = "https://www.stsci.edu/jwst/phase2-public/"
work_dir = "."


def check_apt_file(program_id):
    """
    Check if APT file exists for the given program ID.

    Parameters
    ----------
    program_id : int
        Program ID to check.

    Returns
    -------
    bool
        True if APT file exists, False otherwise.
    """
    apt_file = f"{work_dir}/PPS/APT/{program_id}_APT.xml"
    if not os.path.exists(apt_file):
        return False
    return True


def download_apt(program_id):
    """
    Download and extract APT file for the given program ID.

    Parameters
    ----------
    program_id : int
        Program ID to download APT file for.
    """
    url = f"{base_url}{program_id}.aptx"
    response = requests.get(url)
    if response.status_code == 200:
        # Download the zip file
        with open(f"{work_dir}/PPS/APT/{program_id}_APT.zip", "wb") as f:
            f.write(response.content)

        # Unpack the zip file
        shutil.unpack_archive(
            f"{work_dir}/PPS/APT/{program_id}_APT.zip", f"{work_dir}/PPS/APT"
        )
        os.remove(f"{work_dir}/PPS/APT/{program_id}_APT.zip")

        # Rename the xml file
        os.rename(
            f"{work_dir}/PPS/APT/{program_id}.xml",
            f"{work_dir}/PPS/APT/{program_id}_APT.xml",
        )

        # Remove manifest file
        os.remove(f"{work_dir}/PPS/APT/manifest")

        print(f"Downloaded APT for {program_id}")
    else:
        print(f"Failed to download APT for {program_id}")


def download_vsr(program_id):
    """
    Download VSR file for the given program ID.

    Parameters
    ----------
    program_id : int
        Program ID to download VSR file for.
    """
    url = f"https://www.stsci.edu/jwst-program-info/visits/?program={program_id}&download=&pi=1&referrer=https://www.stsci.edu{program_id}-visit-status.xml"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{work_dir}/PPS/VSR/{program_id}_VSR.xml", "wb") as f:
            f.write(response.content)
        print(f"Downloaded VSR for {program_id}")
    else:
        print(f"Failed to download VSR for {program_id}")


def check_vsr_file(program_id):
    """
    Check if VSR file exists for the given program ID.

    Parameters
    ----------
    program_id : int
        Program ID to check.

    Returns
    -------
    bool
        True if VSR file exists, False otherwise.
    """
    vsr_file = f"{work_dir}/PPS/VSR/{program_id}_VSR.xml"
    if not os.path.exists(vsr_file):
        return False
    return True


def main():
    """
    Loop over program IDs and fetch APT and VSR files.
    """
    # Loop over the program IDs, fetching the APT and VSR files
    program_ids = [2734]
    for program_id in program_ids:
        if not check_apt_file(program_id):
            download_apt(program_id)
        else:
            print(f"APT file for {program_id} already exists")

        if not check_vsr_file(program_id):
            download_vsr(program_id)
        else:
            print(f"VSR file for {program_id} already exists")


if __name__ == "__main__":
    # Make sure the work directory exists
    check_directory(os.path.join(work_dir, "PPS", "APT"))
    check_directory(os.path.join(work_dir, "PPS", "VSR"))

    main()
