import subprocess
import platform
import os

# Detect operating system
os_name = platform.system()

# Define appropriate directories based on OS
if os_name == "Windows":
    analyzed_volatility_output = "O:\\02_volatility_output"
    data_extraction_output = "O:\\04_data_extraction\\"
    volatility_path = "O:\\00_tools\\volatility3-2.8.0\\vol.py"
else:  # Linux/macOS
    analyzed_volatility_output = "/tmp/MemoryInvestigator/02_volatility_output"
    data_extraction_output = "//tmp/MemoryInvestigator/04_data_extraction"
    volatility_path = "/tmp/MemoryInvestigator/00_tools/volatility3-2.8.0/vol.py"

def run_analysis(memory_file, plugins):
    """
    Executes a list of Volatility3 plugins on a given memory dump file and stores the results in JSON format.

    :param memory_file: Path to the memory dump file.
    :param plugins: List of Volatility3 plugins to execute.
    :return: List of execution results.
    """
    results = []
    for plugin in plugins:
        try:
            output_file = os.path.join(analyzed_volatility_output, f"{plugin}.json")
            if os_name == "Windows":
                command = f"powershell -command \"python.exe {volatility_path} -r json -f {memory_file} {plugin} > {output_file}\""
            else:  # Linux/macOS
                command = f"python3 {volatility_path} -r json -f {memory_file} {plugin} > {output_file}"

            subprocess.run(command, shell=True, check=True)
            results.append(f"{plugin} successfully executed.")
        except Exception as e:
            results.append(f"Failure in {plugin}: {str(e)}")
    return results

def run_file_search_analysis(memory_file):
    """
    Runs the 'windows.filescan' plugin to identify files in memory and stores results in JSON format.

    :param memory_file: Path to the memory dump file.
    :return: List containing execution status.
    """
    results = []
    plugin = "windows.filescan"
    output_file = os.path.join(data_extraction_output, f"{plugin}.json")

    if os_name == "Windows":
        command = f"powershell -command \"python.exe {volatility_path} -r json -f {memory_file} {plugin} > {output_file}\""
    else:  # Linux/macOS
        command = f"python3 {volatility_path} -r json -f {memory_file} {plugin} > {output_file}"

    subprocess.run(command, shell=True, check=True)
    results.append(f"{plugin} successfully executed.")
    return results

def run_file_extraction(memory_file, offset):
    """
    Extracts a file from memory at a given virtual offset using the 'windows.dumpfiles' plugin.

    :param memory_file: Path to the memory dump file.
    :param offset: Virtual memory address for file extraction.
    :return: List containing execution status.
    """
    results = []
    plugin = "windows.dumpfiles"

    if os_name == "Windows":
        command = f"powershell -command \"python.exe {volatility_path} -f {memory_file} -o {data_extraction_output} {plugin} --virtaddr {offset}\""
    else:  # Linux/macOS
        command = f"python3 {volatility_path} -f {memory_file} -o {data_extraction_output} {plugin} --virtaddr {offset}"

    subprocess.run(command, shell=True, check=True)
    results.append(f"{plugin} successfully executed.")
    return results

# List of commonly used Volatility3 plugins for memory analysis, add more if needed
GLOBAL_VOLATILITY = [
    "windows.pslist",
    "windows.netstat",
    "windows.netscan",
    "windows.hollowprocesses",
    "windows.processghosting",
    "windows.suspicious_threads",
    "windows.malfind",
    "windows.ldrmodules",
    "windows.svcscan",
    "windows.svcdiff",
    "windows.cmdline",
    "windows.dlllist",
    "windows.getsids",
    "windows.psscan"
]

def modify_global_var():
    """
    Placeholder function for modifying the global plugin list.
    """
    global GLOBAL_VOLATILITY
