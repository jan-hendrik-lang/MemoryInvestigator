import os
import platform
import streamlit as st

# Import utility functions for file handling, tree selection, experimental RAG building, and querying
from utils.file_handler import handle_memory_upload
from utils.select_tree import choose_basic_or_costume_tree
from utils.build_rag_from_books_and_volatility3_data import build_experimental_forensic_rag
from utils.initialize_rag_chat import answer_query
from config import llm_options

# Detect operating system
os_name = platform.system()

# Define appropriate directories based on OS
if os_name == "Windows":
    volatility_output_dir = "O:\\02_volatility_output"
    experimental_rag_dir = "O:\\06_experimental_rag"
else:  # Linux/macOS
    volatility_output_dir = "/tmp/MemoryInvestigator/02_volatility_output"
    experimental_rag_dir = "/tmp/MemoryInvestigator/06_experimental_rag"

vectorstore_dir = os.path.join(experimental_rag_dir, "chroma_store")

# Streamlit page title and description
st.title("Experimental Forensic RAG")
st.caption(f"This module enhances the capabilities of the standard RAG by integrating uploaded PDFs with Volatility3 data output files. The Volatility3 output files are automatically processed from `{volatility_output_dir}` and stored in the vector database. While this approach is experimental, the goal is to achieve deeper insights by linking memory forensics data with document-based information, enabling a more comprehensive forensic analysis.")

# File Upload Mechanism
uploaded_files = st.file_uploader(
    f"File upload may take some time. Alternatively, you can manually transfer the files to `{experimental_rag_dir}`.",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    """
    Uploads multiple files from the Streamlit file uploader to `EXPERIMENTAL_RAG_DIR`.
    """
    os.makedirs(experimental_rag_dir, exist_ok=True)
    for uploaded_file in uploaded_files:
        rag_file_path = handle_memory_upload(uploaded_file, experimental_rag_dir)
        st.success(f"File saved to: {rag_file_path}")

st.caption(f"Choose your preferred LLM and embedding for the analysis. Once the RAG is built, embeddings cannot be changed, but you can switch between LLMs from one company (e.g. `gemini-1.5-pro` to `gemini-2.0-flash-exp`) for further insights. Important: Due to its connection with the Chroma Database, the Streamlit task must be closed before deleting or renewing the RAG and the directory `{vectorstore_dir}` must be deleted manually.")

# Choose a Large Language Model (LLM)
left, middle, right = st.columns(3)
llm_option = left.selectbox(
    "Select an LLM of your choice:",
    options=llm_options,
    index=0
)
if llm_option.startswith("gemini"):
    embedding_options = ["models/embedding-001", "models/embedding-004"]
elif llm_option in ["gpt-4o", "gpt-3.5-turbo", "o1"]:
    embedding_options = ["text-embedding-3-large"]
embedding_option = middle.selectbox(
    "Select an Embedding of your choice:",
    options=embedding_options,
    index=0
)
# API key input field for LLM
api_key = right.text_input("API Key Input:", type="password")

# Build RAG and Chat with LLM, if RAG is available
if api_key:
    try:
        if os.path.exists(vectorstore_dir):
            tree = choose_basic_or_costume_tree()
            if tree is not None:
                with open(tree, 'r', encoding='utf-8') as file:
                    # Read the entire contents of the file
                    json_data = file.read()
                    prompt = st.chat_input("Ask LLM about the analysis results or provide parameters:")
                    if prompt:
                        with st.spinner("Fetching response..."):
                            formatted_prompt = f"{prompt} {json_data}"
                            answer = answer_query(api_key, llm_option, embedding_option, "experimental", formatted_prompt)
                        st.write("**Context:**", answer["context"])
                        st.write("**LLM says:**", answer["answer"])
        else:
            if st.button("Build RAG", use_container_width=True):
                with st.spinner("⏳ Processing... This may take a while. Depending on the complexity, it could take **several hours**. Feel free to grab a coffee ☕ or check back later."):
                    build_experimental_forensic_rag(api_key, llm_option, embedding_option)
                    st.success(f"Experimental RAG successfully built and saved to `{vectorstore_dir}`.")
                    st.rerun()
    except Exception as e:
        st.error(f"Error during query processing: {str(e)}")
else:
    st.error("You must provide an API Key to continue working.")
