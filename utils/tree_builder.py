import json
import os
import platform

# Detect operating system
os_name = platform.system()

# Define appropriate directory for output trees
if os_name == "Windows":
    tree_output_path = "O:\\03_trees"
else:  # Linux/macOS
    tree_output_path = "/tmp/MemoryInvestigator/03_trees"

def load_json_utf16(filepath):
    """
    Loads a JSON file encoded in UTF-16. Falls back to UTF-8 if UTF-16 fails.

    :param filepath: Path to the JSON file.
    :return: Parsed JSON data or an empty list if an error occurs.
    """
    try:
        with open(filepath, "r", encoding="utf-16") as file:
            return json.load(file)
    except (UnicodeError, json.JSONDecodeError):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

def build_hierarchical_tree(selected_files, mode, pid=None):
    """
    Dynamically builds a hierarchical tree, starting with process data from windows.pslist.json.
    Appends data from other selected files to corresponding PID nodes.
    Processes only the specified PID if provided.

    :param selected_files: Dictionary containing filenames and corresponding JSON data.
    :param mode: Specifies the tree type ('costume' or 'basic').
    :param pid: Optional specific Process ID to filter data.
    :return: Generated hierarchical tree structure.
    """
    root = {"name": "System Analysis", "children": []}
    process_nodes = {}  # To hold processes by PID

    # Step 1: Build the base process tree using pslist.json
    if "windows.pslist.json" in selected_files:
        processes_tree = {"name": "Processes", "children": []}
        for process in selected_files["windows.pslist.json"]:
            current_pid = process.get("PID")
            if pid and current_pid != pid:  # Skip if PID does not match
                continue

            ppid = process.get("PPID")
            name = process.get("ImageFileName", "Unknown Process")

            node = {
                "name": name,
                "pid": current_pid,
                "ppid": ppid,
                "children": []
            }
            process_nodes[current_pid] = node

            # Attach to parent or root
            if ppid in process_nodes:
                process_nodes[ppid]["children"].append(node)
            else:
                processes_tree["children"].append(node)
        root["children"].append(processes_tree)

    # Step 2: Append data from other selected files to the process tree
    for filename, records in selected_files.items():
        if filename == "windows.pslist.json":
            continue  # Skip as we already processed this

        file_node = {"name": filename, "children": []}
        fields = field_mapping.get(filename, [])  # Retrieve predefined fields for the file

        for record in records:
            current_pid = record.get("PID") or record.get("Pid") or record.get("pid")
            if pid and current_pid != pid:  # Skip if PID does not match
                continue

            # Prepare only the values from specific fields
            specific_data = {}
            for field in fields:
                if field in record and record[field] not in (None, ""):
                    if field == "SID":
                        specific_data.setdefault("SID", []).append(record[field])
                    elif field == "Args":
                        specific_data.setdefault("Args", []).append(record[field])
                    else:
                        specific_data.setdefault(filename.split('.')[1], {}).update({field: record[field]})

            # Merge into existing PID node
            if current_pid in process_nodes:
                for key, value in specific_data.items():
                    if isinstance(value, list):
                        process_nodes[current_pid].setdefault(key, []).extend(value)
                    elif isinstance(value, dict):
                        process_nodes[current_pid].setdefault(key, {}).update(value)
                    else:
                        process_nodes[current_pid][key] = value
            else:  # Create a new top-level node if no matching PID exists
                new_node = {"name": filename, "pid": current_pid, **specific_data}
                file_node["children"].append(new_node)

        if file_node["children"]:
            root["children"].append(file_node)

    # Step 3: Save the output to the correct directory
    mode_to_path = {
        "costume": "costume_system_analysis_tree.json",
        "basic": "basic_system_analysis_tree.json"
    }
    safe_path = mode_to_path.get(mode, None)
    if not safe_path:
        raise ValueError("Invalid mode. Use 'costume' or 'basic'.")

    output_path = os.path.join(tree_output_path, safe_path)
    try:
        os.makedirs(tree_output_path, exist_ok=True)  # Ensure directory exists
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(root, f, indent=4)
    except Exception as e:
        print(f"Error saving tree: {e}")

    return root

# Predefined field mappings for each JSON file
field_mapping = {
    "windows.cmdline.json": ["Args"],
    "windows.pslist.json": ["PID", "PPID", "ImageFileName", "CreateTime", "ExitTime"],
    "windows.netscan.json": ["Created", "Owner", "Proto", "LocalAddr", "LocalPort", "ForeignAddr", "ForeignPort", "State"],
    "windows.netstat.json": ["Created", "Owner", "Proto", "LocalAddr", "LocalPort", "ForeignAddr", "ForeignPort", "State"],
    "windows.dlllist.json": ["LoadTime", "Path"],
    "windows.getsids.json": ["SID"],
    "windows.hollowprocesses.json": ["Process", "Notes"],
    "windows.ldrmodules.json": ["InInit", "InLoad", "InMem", "MappedPath"],
    "windows.malfind.json": ["Process", "Protection", "Disasm", "Hexdump", "Notes"],
    "windows.processghosting.json": ["Process", "FILE_OBJECT", "DeletePending", "Path"],
    "windows.svcdiff.json": ["Binary", "Binary (Registry)", "Order", "Start", "State", "Dll"],
    "windows.svcscan.json": ["Binary", "Binary (Registry)", "Order", "Start", "State", "Dll"],
    "windows.suspicious_threads": ["TID", "Process", "Context", "Address", "Note"],
}

def load_selected_files(filepaths):
    """
    Load multiple JSON files using UTF-16 format where necessary.

    :param filepaths: List of file paths.
    :return: Dictionary with filenames as keys and parsed JSON data as values.
    """
    selected_files = {}
    for path in filepaths:
        filename = os.path.basename(path)
        selected_files[filename] = load_json_utf16(path)
    return selected_files
