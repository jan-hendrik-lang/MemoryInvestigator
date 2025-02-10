import os
import json
import pandas as pd
import streamlit as st

# Import necessary utility functions for memory file handling and extraction
from utils.volatility_analysis import run_file_search_analysis, run_file_extraction
from utils.file_handler import find_memory_files

# Streamlit page title and description
st.title("Extract Data")
st.caption("Display and search detected files from Volatility3's file scan. Extract specific files to `O:\\04_data_extraction` using the provided virtual offset.")

# Define the file path where Volatility3's file scan results are stored
file_path = "O:\\04_data_extraction\\windows.filescan.json"

# If the file scan JSON does not exist, run the file analysis first
if not os.path.isfile(file_path):
    memory_file = find_memory_files()
    filescan_data = run_file_search_analysis(memory_file)

# Load the file scan JSON output
try:
    with open(file_path, 'r', encoding='utf-16') as file:
        data = json.load(file)
except UnicodeError:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except Exception as e:
    st.error(f"Error reading {file_path}: {e}")


# General search input for filtering results
general_search_term = st.text_input("Enter search term to filter all data:")

try:
    if isinstance(data, list):  # If JSON is an array of objects
        df = pd.DataFrame(data)
    elif isinstance(data, dict):  # If JSON is a dictionary
        df = pd.DataFrame([data])
    else:
        st.warning(f"Unsupported JSON structure in file: {file_path}")

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
        st.write(f"### Results for '{general_search_term}' in {file_path}:")
        st.dataframe(filtered_df)
    else:
        st.write(f"### Data from {file_path}")
        st.dataframe(df)

except Exception as e:
    st.error(f"Error processing {file_path}: {e}")

# Input field for specifying the offset for file extraction
offset = st.number_input("Extract files to `O:\\04_data_extraction\\` using the offset from the given table.", step=1, value=0)

# Button to trigger file extraction
if st.button("Extract File", use_container_width=True):
    with st.spinner("Extracting File..."):
        memory_file = find_memory_files()
        extracted_file = run_file_extraction(memory_file, offset)
        st.success("Data extracted.")
