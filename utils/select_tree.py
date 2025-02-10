import os

def choose_basic_or_costume_tree():
    """
    Determines which system analysis tree file to use, prioritizing the customized tree if available.

    :return: The path to the selected JSON tree file, or None if no tree exists.
    """
    # Define the directory where tree files are stored
    directory = r"O:\03_trees"
    file1 = "basic_system_analysis_tree.json"
    file2 = "costume_system_analysis_tree.json"

    # Construct full file paths
    file1_tree = os.path.join(directory, file1)
    file2_tree = os.path.join(directory, file2)

    # Check if the files exist
    file1_exists = os.path.isfile(file1_tree)
    file2_exists = os.path.isfile(file2_tree)

    # Logic to handle the presence of the files, prioritize returning the customized tree if available
    if file1_exists and file2_exists:
        return file2_tree
    elif file1_exists:
        return file1_tree
    elif file2_exists:
        return file2_tree
    else:
        return None