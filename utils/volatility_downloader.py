import subprocess
import requests
import platform
import os
from io import BytesIO
import zipfile

# Detect operating system
os_name = platform.system()

# Define the appropriate target directory based on OS
if os_name == "Windows":
    target_dir = "O:/00_tools"
else:  # Linux/macOS
    target_dir = "/tmp/MemoryInvestigator/00_tools"  # Change this if needed


def volatility_download():
    """
    Downloads and installs Volatility3 by fetching the latest release archive from GitHub,
    extracting it to the designated directory, and installing its dependencies.
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

    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Download and extract the Volatility3 release
    download_and_extract(repo_url, target_dir)

    # Step 1: Uninstall old Yara package if installed
    if os_name == "Windows":
        uninstall_yara = "powershell -command pip uninstall yara -y"
    else:  # Linux/macOS
        uninstall_yara = "pip uninstall yara -y"

    subprocess.run(uninstall_yara, shell=True, check=True)

    # Step 2: Install Volatility3 dependencies from the extracted requirements.txt file
    requirements_file = os.path.join(target_dir, "volatility3-2.8.0", "requirements.txt")

    if os_name == "Windows":
        install_vol_command = f"powershell -command \"pip install -r {requirements_file}\""
    else:  # Linux/macOS
        install_vol_command = f"pip install -r {requirements_file}"

    subprocess.run(install_vol_command, shell=True, check=True)
