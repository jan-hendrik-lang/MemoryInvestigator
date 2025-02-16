import os
import platform

# Detect operating system
os_name = platform.system()

# Define memory dump directory based on OS
if os_name == "Windows":
    memory_dump_dir = "O:\\01_memory"
else:  # Linux/macOS
    memory_dump_dir = "/tmp/MemoryInvestigator/01_memory"

# Allowed file extensions for memory dumps
memory_extensions = (".vmem", ".raw")

def handle_memory_upload(uploaded_file, upload_dir=memory_dump_dir):
    """
    Handles the upload of memory dump files by saving them to a predefined directory.

    :param uploaded_file: A file-like object uploaded via Streamlit's file_uploader.
    :param upload_dir: The directory where the uploaded file should be saved.
    :return: The file path where the uploaded file is stored.
    """
    # Ensure the directory exists
    os.makedirs(upload_dir, exist_ok=True)

    # Save the file
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

def find_memory_files(directory=memory_dump_dir, extensions=memory_extensions):
    """
    Searches for memory dump files in the specified folder and returns the first matching file.

    :param directory: The folder to search for memory dump files.
    :param extensions: A tuple of allowed file extensions.
    :return: Full path of the first found memory dump file, or None if no files are found.
    """
    if not os.path.exists(directory):
        return None

    for file in os.listdir(directory):
        if file.endswith(extensions):
            return os.path.join(directory, file)

    return None  # Return None if no file is found
