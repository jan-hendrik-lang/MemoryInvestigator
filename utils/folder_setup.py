import os
import tempfile
import shutil
import json

# Global variable to store the temporary directory path
TEMP_DIR = None

# List of subdirectories to be created within the temporary drive
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

# Function to create a temporary drive and initialize subdirectories
def create_drive():
    """
    Creates a temporary virtual drive and initializes necessary subdirectories.

    :return: A success message indicating the creation of the drive and folders.
    """
    global TEMP_DIR

    # Check if O: drive exists; if not, create a temporary directory and assign it to O:
    if not os.path.exists("O:"):
        TEMP_DIR = tempfile.mkdtemp()
        os.system(f"subst O: {TEMP_DIR}")

    # Verify if the virtual drive was successfully created
    if not os.path.exists("O:"):
        return "Failed to create temporary directory."

    # Create necessary subdirectories
    for folder in SUBDIRECTORIES:
        folder_path = os.path.join("O:\\", folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Create an empty settings file
    settings_file_path = os.path.join("O:\\", "settings.json")
    settings_data = {}
    with open(settings_file_path, "w") as file:
        json.dump(settings_data, file, indent=4)

    return f"Drive O: and Folders are created."

# Function to remove the virtual drive and all its contents
def remove_drive():
    """
    Deletes the temporary virtual drive and its subdirectories.

    :return: A message indicating whether the drive was successfully removed.
    """
    global TEMP_DIR

    if os.path.exists("O:"):
        os.system("subst O: /D")
        if TEMP_DIR:
            try:
                shutil.rmtree(TEMP_DIR, ignore_errors=True)  # Delete the temporary directory
                TEMP_DIR = None
                return "Drive disconnected and Contents deleted."
            except Exception as e:
                return f"Failure while disconnecting Drive: {str(e)}"
        return "Drive disconnected."


