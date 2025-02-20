import os
import subprocess
import platform
import streamlit as st

# Import utility functions for Chat handling, and tree building
from utils.chat_handler import handle_llm_chat
from utils.tree_builder import build_hierarchical_tree, load_selected_files
from config import llm_options

# Detect operating system
os_name = platform.system()

# Define appropriate directories based on OS
if os_name == "Windows":
    volatility_output_dir = "O:\\02_volatility_output"
    tree_file_path = "O:\\03_trees\\costume_system_analysis_tree.json"
else:  # Linux/macOS
    volatility_output_dir = "/tmp/MemoryInvestigator/02_volatility_output"
    tree_file_path = "/tmp/MemoryInvestigator/03_trees/costume_system_analysis_tree.json"

# Streamlit page title and description
st.title("Analysis with Tree-of-Table")
st.caption("This module enables analysis by combining information from Volatility3 in a tree structure with an LLM. A basic tree is automatically generated to provide an initial overview of the data. Users can also create a customized tree tailored to their needs, such as focusing on a specific PID for more detailed analysis. The tree is automatically included in the user prompt. If the tree is too large for a single context window and so a smaller chunk size is required, it can be split into multiple trees, which will be analyzed separately and summarized.")

# Show and select JSON Fields
json_files = [f for f in os.listdir(volatility_output_dir) if f.endswith('.json')]

# User selection for JSON files and optional Process ID
left, right = st.columns(2)
selected_files = left.multiselect(
    "Select JSON files for analysis:",
    options=json_files,
    default="windows.pslist.json"
)
pid = right.number_input("Enter a specific Process ID if desired:", step=1)

# Button to build a custom tree
left, right = st.columns(2)
if left.button("Build a custom Tree", use_container_width=True):
    with st.spinner("Building a specific Tree..."):
        selected_filepaths = [os.path.join(volatility_output_dir, file) for file in selected_files]
        selected_files = load_selected_files(selected_filepaths)
        mode = "costume"
        hierarchical_tree = build_hierarchical_tree(selected_files, mode, pid)
        st.success("Custom tree built successfully!")

# Allow opening and modifying the generated tree file
if os.path.isfile(tree_file_path):
    if right.button("Show and manipulate Tree", use_container_width=True):
        if os_name == "Windows":
            command = f"powershell -command \"notepad {tree_file_path}\""
        elif os_name == "Linux":
            command = f"xdg-open {tree_file_path}"
        elif os_name == "Darwin":  # macOS
            command = f"open {tree_file_path}"
        else:
            command = None

        if command:
            subprocess.run(command, shell=True, check=True)
            st.write(f"Opening file: {tree_file_path}")

# Choose a Large Language Model (LLM)
left, middle, right = st.columns(3)
llm_option = left.selectbox(
    "Select an LLM of your choice:",
    options=llm_options,
    index=0
)

# API key input fields
api_llm_key = middle.text_input("API LLM Key Input:", type="password")
number_of_divided_jsons = right.number_input("Divide JSON file into multiple files:", step=1, value=0)

prompt = st.chat_input("Ask the LLM about the analysis results or provide parameters:")

if api_llm_key:
    try:
        handle_llm_chat(llm_option, api_llm_key, number_of_divided_jsons, prompt)
    except Exception as e:
        st.error(f"Error during query processing: {str(e)}")
else:
    st.error("You must provide an API LLM Key to continue working.")
