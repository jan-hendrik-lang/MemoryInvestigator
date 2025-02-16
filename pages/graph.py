import json
import os
import platform
import streamlit as st
from streamlit_agraph import agraph, Config, Node, Edge

# Detect operating system
os_name = platform.system()

# Define appropriate file path based on OS
if os_name == "Windows":
    file_path = "O:\\02_volatility_output\\windows.pslist.json"
else:  # Linux/macOS
    file_path = "/tmp/MemoryInvestigator/02_volatility_output/windows.pslist.json"

# Streamlit page title and description
st.title("Graph Generator")
st.caption("Visualize PIDs in a graph, zoom in or out, and search for a specific PID.")

def build_process_tree(data, highlight_pid=None):
    """
    Build nodes and edges for the process tree visualization.

    :param data: List of process dictionaries.
    :param highlight_pid: PID to highlight in the graph.
    :return: Tuple (nodes, edges).
    """
    process_map = {process['PID']: process for process in data}
    nodes = []
    edges = []

    for process in data:
        pid = process['PID']
        ppid = process['PPID']
        name = process['ImageFileName']

        # Highlight specific node if it matches highlight_pid
        node_color = "#000000" if highlight_pid == pid else "#B3EBF2"  # Default and highlight colors

        # Add node for the process
        nodes.append(Node(id=str(pid), label=f"{name} (PID: {pid})", color=node_color))

        # Add edge to the parent process if it exists
        if ppid in process_map:
            edges.append(Edge(source=str(ppid), target=str(pid)))

    return nodes, edges

# Load JSON data
try:
    with open(file_path, 'r', encoding='utf-16') as file:
        data = json.load(file)
except (UnicodeError, json.JSONDecodeError):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
        st.stop()

# Initialize session state for PID highlighting
if "highlight_pid" not in st.session_state:
    st.session_state["highlight_pid"] = None

# User input for searching a specific PID
search_pid = st.text_input("Enter PID to search and highlight (leave blank for full tree):")

# Update session state dynamically based on user input
if search_pid.isdigit():
    st.session_state["highlight_pid"] = int(search_pid)
else:
    st.session_state["highlight_pid"] = None

# Generate nodes and edges for process tree visualization
nodes, edges = build_process_tree(data, st.session_state["highlight_pid"])

# Configure the graph visualization settings
config = Config(
    width=750,
    height=800,
    directed=True,
    nodeHighlightBehavior=True,
    collapsible=True,
    physics=False,
    hierarchical=True,
    direction="LR",
    sortMethod="directed",
    shakeTowards="Leaves",
)

# Display the interactive graph
agraph(nodes=nodes, edges=edges, config=config)
