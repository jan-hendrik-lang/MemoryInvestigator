import os

def handle_memory_upload(uploaded_file, upload_dir):
    """
    Handles the upload of memory dump files by saving them to a predefined directory.

    :param uploaded_file: A file-like object uploaded via Streamlit's file_uploader.
    :param upload_dir: The directory where the uploaded file should be saved.
    :return: The file path where the uploaded file is stored.
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the file to the upload directory
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

def find_memory_files():
    """
    Searches for memory dump files in the specified folder and returns the first matching file.

    :return: Full path of the first found memory dump file, or None if no files are found.
    """
    for file in os.listdir(folder_path):
        if file.endswith(extensions):
            return os.path.join(folder_path, file)


# Folder to search for memory files
folder_path = r"O:\01_memory"

# Allowed file extensions for memory dumps
extensions = (".vmem", ".raw")