import subprocess

# Define output directories for analysis and data extraction
ANALYZED_VOLATILITY_OUTPUT = "O:\\02_volatility_output"
DATA_EXTRACTION_OUTPUT = "O:\\04_data_extraction\\"

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
            command =  f"powershell -command \"python.exe O:\\00_tools\\volatility3-2.8.0\\vol.py -r json -f {memory_file} {plugin} > {ANALYZED_VOLATILITY_OUTPUT}\\{plugin}.json\""
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
    command =  f"powershell -command \"python.exe O:\\00_tools\\volatility3-2.8.0\\vol.py -r json -f {memory_file} {plugin} > {DATA_EXTRACTION_OUTPUT}\\{plugin}.json\""
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
    command =  f"powershell -command \"python.exe O:\\00_tools\\volatility3-2.8.0\\vol.py -f {memory_file} -o {DATA_EXTRACTION_OUTPUT} {plugin} --virtaddr {offset} \""
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
    "windows.getsids"
]

def modify_global_var():
    """
    Placeholder function for modifying the global plugin list.
    """
    global GLOBAL_VOLATILITY
