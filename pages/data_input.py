import os
import streamlit as st
import json

# Import utility functions for handling memory files, running analysis, and building trees
from utils.file_handler import handle_memory_upload, find_memory_files
from utils.volatility_analysis import run_analysis, GLOBAL_VOLATILITY, run_file_search_analysis
from utils.tree_builder import build_hierarchical_tree, load_selected_files

# Streamlit page title and description
st.title("Data Input")
st.caption("Upload memory files and enter project details on this page. If a memory file is available, you can start exploring memory data and generating insights. For more information, visit the [`Help Page`](./help).")

# File uploader allowing multiple memory file types
uploaded_files = st.file_uploader(
    "File upload may take some time. Alternatively, you can manually transfer the files to `O:\\01_memory`.",
    type=["raw", "vmem", "vmsn"],
    accept_multiple_files=True  # Allow multiple files
)

# Handle uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = handle_memory_upload(uploaded_file, "O:\\01_memory")
        st.success(f"File saved to: {file_path}")

# Function for user data input
def input_data():
    """
    Loads previously saved settings if available and provides input fields
    for the user to enter project-related information.
    """
    try:
        with open("O:\\settings.json", "r") as json_file:
            saved_data = json.load(json_file)
    except FileNotFoundError:
        saved_data = {}

    name = st.text_input("Enter your Name:", value=saved_data.get("name", "Joe Public"))
    project_name = st.text_input("Enter Project Name:", value=saved_data.get("project_name", "CEO Notebook Analysis"))
    date = st.date_input("Select Date", value=saved_data.get("date", "today"))
    txt = st.text_area("Notes", value=saved_data.get("notes", "e.g. Windows 11 24h2 with possible intruder"))
    return name, project_name, date, txt

# Function to save user input to JSON file
def save_to_json(name, project_name, date, txt):
    """
    Saves the user-provided project settings to a JSON file.
    """
    settings_data = {
        "name": name,
        "project_name": project_name,
        "date": str(date),  # Convert date to string for JSON serialization
        "notes": txt
    }
    with open("O:\\settings.json", "w") as json_file:
        json.dump(settings_data, json_file, indent=4)

# Capture user input
name, project_name, date, txt = input_data()

left, right = st.columns(2)

# Save button to store project settings in JSON
if left.button("Save Project Settings", use_container_width=True):
    save_to_json(name, project_name, date, txt)
    st.success("Input Data has been saved to `settings.json`.")

# Define memory file directory path
directory_path = r"O:\01_memory"

try:
    # Check if any memory files exist in the target directory
    if any(file.lower().endswith(('.raw', '.vmem', '.vmsn')) for file in os.listdir(directory_path)):
        st.success("Valid memory files found in the directory.")
        # Check if a hierarchical tree has already been generated
        if any(file.lower().endswith('.json') for file in os.listdir("O:\\03_trees")):
            st.success("A valid tree was found in the directory. You can now start digging deeper.")
        else:
            st.error("No valid tree found. Please build one by clicking on `Analyze Data and Build a Basic Tree`.")
        # Button to trigger analysis and tree-building
        if right.button("Analyze Data and Build a Basic Tree", use_container_width=True):
            memory_file = find_memory_files()
            with st.spinner("Analyzing your memory dump..."):
                run_analysis(memory_file, GLOBAL_VOLATILITY)
                run_file_search_analysis(memory_file)

            with st.spinner("Building a basic tree."):
                output_path = "O:\\02_volatility_output\\windows.pslist.json"
                if os.path.exists(output_path):
                    selected_filepaths = [output_path]
                    selected_files = load_selected_files(selected_filepaths)
                    mode = "basic"
                    hierarchical_tree = build_hierarchical_tree(selected_files, mode, pid=None)
                    st.success("Data analyzed and simple tree built!")
                else:
                    st.error("Output file not found. Ensure the drive is connected and the analysis ran successfully.")

            # Trigger a rerun
            st.rerun()
    else:
        st.warning("No valid memory files found in the directory.")

except Exception as e:
    st.error(f"Drive O: cannot be accessed. Renew or restart the environment.")
