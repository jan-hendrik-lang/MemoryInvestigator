import os
import json
import platform
import pandas as pd
import streamlit as st

# Detect operating system
os_name = platform.system()

# Define appropriate folder path based on OS
if os_name == "Windows":
    folder_path = "O:\\02_volatility_output"
else:  # Linux/macOS
    folder_path = "/tmp/MemoryInvestigator/02_volatility_output"

# Streamlit page title and description
st.title("Display Data")
st.caption("Display data from the memory file by selecting a Volatility3 module and searching within a specific column or across all columns.")

# Ensure directory exists
if not os.path.exists(folder_path):
    st.error(f"Directory {folder_path} does not exist.")
    st.stop()

# Retrieve all JSON files in the directory
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

# Set a default selection if 'windows.pslist.json' is present
default_file = ["windows.pslist.json"] if "windows.pslist.json" in json_files else []

# Allow users to select JSON files for analysis
selected_files = st.multiselect(
    "Select JSON files for analysis:",
    options=json_files,
    default=default_file
)

# General search field for filtering across all data columns
general_search_term = st.text_input("Enter search term to filter all data:")

if selected_files:
    # Iterate through selected JSON files and display their contents
    for file_name in selected_files:
        file_path = os.path.join(folder_path, file_name)

        # Read JSON file with UTF-16 encoding (fallback to UTF-8)
        try:
            with open(file_path, 'r', encoding='utf-16') as file:
                data = json.load(file)
        except (UnicodeError, json.JSONDecodeError):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            except Exception as e:
                st.error(f"Error reading {file_name}: {e}")
                continue

        # Convert JSON data to Pandas DataFrame
        try:
            if isinstance(data, list):  # If JSON is an array of objects
                df = pd.DataFrame(data)
            elif isinstance(data, dict):  # If JSON is a dictionary
                df = pd.DataFrame([data])
            else:
                st.warning(f"Unsupported JSON structure in file: {file_name}")
                continue

            # Reorder DataFrame columns for better readability
            lowercase_columns = {col.lower(): col for col in df.columns}  # Map lowercase to Original
            desired_order_lower = ["pid", "ppid", "imagefilename"]
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
                st.write(f"### Results for '{general_search_term}' in {file_name}:")
                st.dataframe(filtered_df)
            else:
                st.write(f"### Data from {file_name}")
                st.dataframe(df)

            # Enable optional column-specific filtering
            if st.checkbox(f"Enable column-specific filtering for {file_name}"):
                column_name = st.selectbox(f"Select column to filter in {file_name}:", df.columns, key=f"col-{file_name}")
                column_filter = st.text_input(f"Enter value to filter {column_name}:", key=f"filter-{file_name}")
                if column_filter:
                    filtered_column_df = df[df[column_name].astype(str).str.contains(column_filter, case=False, na=False)]
                    st.write(f"### Results for filter '{column_filter}' in column '{column_name}' of {file_name}:")
                    st.dataframe(filtered_column_df)

        except Exception as e:
            st.error(f"Error processing {file_name}: {e}")
else:
    st.info("Please select at least one JSON file to display.")
