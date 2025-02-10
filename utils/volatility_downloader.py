import subprocess

import requests
from io import BytesIO
import zipfile

def volatility_download():
    """
    Downloads and installs Volatility3 by fetching the latest release archive from GitHub,
    extracting it to the designated directory, uninstall old Yara package if installed,
    and installing its dependencies.
    """
    def download_and_extract(repo_url, target_directory):
        """
        Downloads a ZIP archive from a given repository URL and extracts it to the specified directory.

        :param repo_url: URL of the ZIP archive to download.
        :param target_directory: Directory where the extracted files will be stored.
        """
        response = requests.get(repo_url, stream=True)
        if response.status_code == 200:
            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(target_directory)
        else:
            return f"Download failed with status code {response.status_code}"

    # Define the repository URL for the Volatility3 ZIP archive
    repo_url = "https://github.com/volatilityfoundation/volatility3/archive/refs/tags/v2.8.0.zip"
    target_directory = "O:/00_tools"
    # Download and extract the Volatility3 release
    download_and_extract(repo_url, target_directory)

    # Step 1: Uninstall old Yara package if installed
    uninstall_yara = f"powershell -command pip uninstall yara -y"
    subprocess.run(uninstall_yara, shell=True, check=True)

    # Step 2: Install Volatility3 dependencies from the extracted requirements.txt file
    install_vol_command = f"powershell -command \"pip install -r O:\\00_tools\\volatility3-2.8.0\\requirements.txt\""
    subprocess.run(install_vol_command, shell=True, check=True)
