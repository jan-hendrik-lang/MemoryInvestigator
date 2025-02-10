import streamlit as st

# Import utility functions for file handling, tree selection, experimental RAG building, and querying
from utils.file_handler import handle_memory_upload
from utils.select_tree import choose_basic_or_costume_tree
from utils.build_rag_from_books_and_volatility3_data import build_experimental_forensic_rag
from utils.initialize_rag_chat import answer_query

# Streamlit page title and description
st.title("Experimental Forensic RAG")
st.caption("This module enhances the capabilities of the standard RAG by integrating uploaded PDFs with Volatility3 data output files. The Volatility3 output files are automatically processed from `O:\\02_volatility_output` and stored in the vector database. While this approach is experimental, the goal is to achieve deeper insights by linking memory forensics data with document-based information, enabling a more comprehensive forensic analysis.")

# File Upload Mechanism
uploaded_files = st.file_uploader(
    "File upload may take some time. Alternatively, you can manually transfer the files to `O:\\06_experimental_rag`.",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    """
    Uploads multiple files from the Streamlit file uploader to 'O:\\06_experimental_rag'.
    """
    for uploaded_file in uploaded_files:
        rag_file_path = handle_memory_upload(uploaded_file, "O:\\06_experimental_rag")
        st.success(f"File saved to: {rag_file_path}")

st.caption("Choose your preferred LLM and embedding for the analysis. Once the RAG is built, embeddings cannot be changed, but you can switch between LLMs from one company (e.g. `gemini-1.5-pro` to `gemini-2.0-flash-exp`) for further insights. Important: Due to its connection with the Chroma Database, the Streamlit task must be closed before deleting or renewing the RAG and the directory `O:\\06_experimental_rag\\chroma_store` must be deleted manually.")

# Choose a Large Language Model (LLM)
left, middle, right = st.columns(3)
llm_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.0-flash-thinking-exp", "chatgpt-4o-latest", "gpt-3.5-turbo", "o1-preview"]
llm_option = left.selectbox(
    "Select an LLM of your choice:",
    options=llm_options,
    index=0
)
if llm_option.startswith("gemini"):
    embedding_options = ["models/embedding-001", "models/embedding-004", "text-embedding-004"]
elif llm_option == "chatgpt-4o-latest" or llm_option == "gpt-3.5-turbo" or llm_option == "o1-preview":
    embedding_options = ["text-embedding-3-large"]
embedding_option = middle.selectbox(
    "Select an Embedding of your choice:",
    options=embedding_options,
    index=0
)
# API key input fields for LLM and LangChain authentication
api_key = right.text_input("API Key Input:", type="password")

# Build RAG if API keys are provided
if api_key:
    if st.button("Build RAG", use_container_width= True):
        with st.spinner("Building RAG..."):
            build_experimental_forensic_rag(api_key, llm_option, embedding_option)
            st.success("RAG built!")
else:
    st.error("You must provide API LLM Key to continue working.")

# If no RAG available, built RAG and also Chat with the RAG if API keys are available
if api_key:
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
        st.error("Please build a tree to analyze the memory.")