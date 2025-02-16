import os
import json
import platform
import pandas as pd
import streamlit as st

# Import necessary utility functions for memory file handling and extraction
from utils.volatility_analysis import run_file_search_analysis, run_file_extraction
from utils.file_handler import find_memory_files

# Detect operating system
os_name = platform.system()

# Define appropriate file path based on OS
if os_name == "Windows":
    data_extraction_dir = "O:\\04_data_extraction"
else:  # Linux/macOS
    data_extraction_dir = "/tmp/MemoryInvestigator/04_data_extraction"

FILE_PATH = os.path.join(data_extraction_dir, "windows.filescan.json")

# Streamlit page title and description
st.title("Extract Data")
st.caption(f"Display and search detected files from Volatility3's file scan. Extract specific files to `{data_extraction_dir}` using the provided virtual offset.")

# If the file scan JSON does not exist, run the file analysis first
if not os.path.isfile(FILE_PATH):
    memory_file = find_memory_files()
    filescan_data = run_file_search_analysis(memory_file)

# Load the file scan JSON output
try:
    with open(FILE_PATH, 'r', encoding='utf-16') as file:
        data = json.load(file)
except (UnicodeError, json.JSONDecodeError):
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        st.error(f"Error reading {FILE_PATH}: {e}")
        st.stop()

# General search input for filtering results
general_search_term = st.text_input("Enter search term to filter all data:")

try:
    if isinstance(data, list):  # If JSON is an array of objects
        df = pd.DataFrame(data)
    elif isinstance(data, dict):  # If JSON is a dictionary
        df = pd.DataFrame([data])
    else:
        st.warning(f"Unsupported JSON structure in file: {FILE_PATH}")

    # Reorder DataFrame columns to prioritize specific fields
    lowercase_columns = {col.lower(): col for col in df.columns}  # Map lowercase to Original
    desired_order_lower = ["Name"]
    present_columns = [lowercase_columns[col] for col in desired_order_lower if col in lowercase_columns]
    reordered_columns = present_columns + [col for col in df.columns if col not in present_columns]
    df = df[reordered_columns]

    # Apply general search across all columns
    if general_search_term:
        filtered_df = df[
            df.apply(
                lambda row: row.astype(str).str.contains(general_search_term, case=False, na=False).any(),
                axis=1
            )
        ]
        st.write(f"### Results for '{general_search_term}' in {FILE_PATH}:")
        st.dataframe(filtered_df)
    else:
        st.write(f"### Data from {FILE_PATH}")
        st.dataframe(df)

except Exception as e:
    st.error(f"Error processing {FILE_PATH}: {e}")

# Input field for specifying the offset for file extraction
offset = st.number_input(f"Extract files to `{data_extraction_dir}` using the offset from the given table.", step=1, value=0)

# Button to trigger file extraction
if st.button("Extract File", use_container_width=True):
    with st.spinner("Extracting File..."):
        memory_file = find_memory_files()
        extracted_file = run_file_extraction(memory_file, offset)
        st.success("Data extracted.")
