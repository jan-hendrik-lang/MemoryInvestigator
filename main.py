import streamlit as st
import os
import time
import keyboard
import psutil

# Import utility functions for drive management and Volatility3 setup
from utils.folder_setup import remove_drive, create_drive
from utils.volatility_downloader import volatility_download

def main():
    """
    Main function to initialize and manage the Streamlit app.
    Ensures that the required environment is set up, including creating
    a virtual drive (O:\) and downloading necessary Volatility3 files.
    """
    # Create O: if it´s not exists already
    if not os.path.exists("O:\\"):
        create_drive()
        volatility_download()

    def build_pages():
        """
        Function to dynamically build the navigation pages of the app
        based on whether a basic system analysis has been performed.
        """
        # Defined pages based on whether analysis data exists
        if os.path.isfile("O:\\03_tree\\basic_system_analysis_tree.json") or os.path.isfile("O:\\02_volatility_output\\windows.pslist.json"):
            pages = {
                "Environment": [
                    st.Page("pages/data_input.py", title="Data Input"),
                ],
                "Simple Analysis": [
                    st.Page("pages/display_data.py", title="Display Data as Table"),
                    st.Page("pages/graph.py", title="Display Data as Graph"),
                    st.Page("pages/extract_data.py", title="Extract Data"),
                ],
                "Artificial Intelligence Analysis": [
                    st.Page("pages/tree_of_table.py", title="Analysis with Tree-of-Table"),
                    st.Page("pages/standard_rag.py", title="Analysis with Standard RAG"),
                    st.Page("pages/experimental_forensic_rag.py", title="Analysis with Experimental Forensic RAG"),
                    st.Page("pages/report.py", title="Generate Report"),
                ],
                "Help": [
                    st.Page("pages/help.py", title="Help"),
                ],
            }
        else:
            # If no analysis has been run, only show basic pages
            pages = {
                "Environment": [
                    st.Page("pages/data_input.py", title="Data Input"),
                ],
                "Help": [
                    st.Page("pages/help.py", title="Help"),
                ],
            }

        # Sidebar button to reset environment
        if st.sidebar.button("Renew Environment", type="primary", use_container_width=True):
            remove_drive()
            create_drive()
            volatility_download()
            st.switch_page("pages/data_input.py")

        # Sidebar button to delete session and shut down the app
        if st.sidebar.button("Delete Session", type="primary", use_container_width=True, on_click=lambda: st.toast("The session with the O: drive and all its contained files will be deleted, and the app itself will be shut down.")):
            remove_drive()
            # Give a bit of delay for user experience
            time.sleep(5)
            # Close streamlit browser tab
            keyboard.press_and_release('ctrl+w')
            # Terminate streamlit python process
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()

        pg = st.navigation(pages)
        pg.run()
    build_pages()


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()