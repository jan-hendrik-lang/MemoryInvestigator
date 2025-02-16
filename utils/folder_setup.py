import os
import tempfile
import shutil
import json

def define_base_drive(os_name):
    if os_name == "Windows":
        base_drive = "O:"
    else:  # Linux/macOS
        base_drive = "/tmp/MemoryInvestigator"
    return base_drive

# List of subdirectories to be created within the virtual drive
SUBDIRECTORIES = [
    "00_tools",
    "01_memory",
    "02_volatility_output",
    "03_trees",
    "04_data_extraction",
    "05_standard_rag",
    "06_experimental_rag",
    "07_help",
]

# Global variable to store the temporary directory path
temp_dir = None

def create_drive(os_name):
    """
    Creates a virtual drive and initializes necessary subdirectories.

    :return: A success message indicating the creation of the drive and folders.
    """
    global temp_dir

    base_drive = define_base_drive(os_name)

    if os_name == "Windows":
        # Check if O: drive exists; if not, create a temporary directory and assign it to O:
        if not os.path.exists(base_drive):
            temp_dir = tempfile.mkdtemp()
            os.system(f"subst {base_drive} {temp_dir}")

        # Verify if the virtual drive was successfully created
        if not os.path.exists(base_drive):
            return "Failed to create temporary directory."
    else:  # Linux/macOS
        # Create the mount point if it doesn't exist
        os.makedirs(base_drive, exist_ok=True)
        temp_dir = base_drive

    # Create necessary subdirectories
    for folder in SUBDIRECTORIES:
        folder_path = os.path.join(base_drive, folder)
        os.makedirs(folder_path, exist_ok=True)

    # Create an empty settings file
    settings_file_path = os.path.join(base_drive, "settings.json")
    settings_data = {}
    with open(settings_file_path, "w") as file:
        json.dump(settings_data, file, indent=4)

    return f"Drive {base_drive} and Folders are created."

def remove_drive(os_name):
    """
    Deletes the virtual drive and its subdirectories.

    :return: A message indicating whether the drive was successfully removed.
    """
    global temp_dir

    base_drive = define_base_drive(os_name)

    if os_name == "Windows":
        if os.path.exists(base_drive):
            os.system(f"subst {base_drive} /D")
            if temp_dir:
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)  # Delete the temporary directory
                    temp_dir = None
                    return "Drive disconnected and contents deleted."
                except Exception as e:
                    return f"Failure while disconnecting Drive: {str(e)}"
            return "Drive disconnected."
    else:  # Linux/macOS
        if os.path.exists(base_drive):
            try:
                shutil.rmtree(base_drive, ignore_errors=True)
                return "Drive contents deleted."
            except Exception as e:
                return f"Failure while removing drive contents: {str(e)}"
