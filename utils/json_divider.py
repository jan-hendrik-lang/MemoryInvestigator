import os
import platform
import streamlit as st

# Detect operating system
os_name = platform.system()

# Define appropriate temp directory for JSON parts
if os_name == "Windows":
    default_save_path = "O:\\03_trees\\temp"
else:  # Linux/macOS
    default_save_path = "/tmp/MemoryInvestigator/03_trees/temp"  # Adjust as needed

def divide_json(num_parts, json_file_path, save_path=default_save_path):
    """
    Splits a JSON file into smaller parts and saves them as separate files.

    :param num_parts: Number of smaller JSON files to create.
    :param json_file_path: Path to the original JSON file.
    :param save_path: Directory where the divided JSON files will be stored.
    :return: List of file paths for the divided JSON files.
    """
    # Ensure the output directory exists
    os.makedirs(save_path, exist_ok=True)

    # Validate input parameters
    if num_parts <= 0:
        st.error("Number of parts must be greater than zero.")
        return []

    if not os.path.exists(json_file_path):
        st.error("JSON file not found.")
        return []

    divided_data = []

    # Read the JSON file and split it into chunks
    with open(json_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        total_lines = len(lines)
        chunk_size = max(1, total_lines // num_parts)

        for i in range(num_parts):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i < num_parts - 1 else total_lines
            chunk = lines[start_index:end_index]
            file_name = os.path.join(save_path, f"temp_{i + 1:02d}.json")

            # Write chunk to a new file
            with open(file_name, "w", encoding="utf-8") as f:
                f.writelines(chunk)

            divided_data.append(file_name)

    return divided_data
