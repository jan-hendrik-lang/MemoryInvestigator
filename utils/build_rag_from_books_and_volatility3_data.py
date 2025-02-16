import os
import platform
import shutil

from langchain_community.document_loaders import PyPDFLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

# Detect operating system
os_name = platform.system()

# Define appropriate directories based on OS
if os_name == "Windows":
    volatility_data_dir = "O:\\02_volatility_output"
    rag_data_dir = "O:\\06_experimental_rag"
else:  # Linux/macOS
    volatility_data_dir = "/tmp/MemoryInvestigator/02_volatility_output"
    rag_data_dir = "/tmp/MemoryInvestigator/06_experimental_rag"

VECTORSTORE_DIR = os.path.join(rag_data_dir, "chroma_store")

def convert_utf16_to_utf8_json(input_file_path, output_file_path):
    """
    Converts a JSON file from UTF-16 encoding to UTF-8.

    :param input_file_path: Path to the input UTF-16 JSON file.
    :param output_file_path: Path to the output UTF-8 JSON file.
    """
    try:
        with open(input_file_path, 'r', encoding='utf-16') as infile:
            content = infile.read()
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(content)
    except UnicodeError:
        # If file is already UTF-8, just copy it
        shutil.copy(input_file_path, output_file_path)

def build_experimental_forensic_rag(api_key, llm_option, embedding_option):
    """
    Builds an experimental forensic RAG model by integrating Volatility3 JSON output and uploaded PDFs.

    :param api_key: API key for LLM and Embeddings.
    :param llm_option: Selection if Google GenAI or OpenAI Model.
    :param embedding_option: Selection of embedding model.
    :return: A retriever object for querying the generated vector store.
    """

    # Initialize embedding model
    if llm_option.startswith("gemini"):
        os.environ["GOOGLE_API_KEY"] = api_key
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_option)
    elif llm_option in ["chatgpt-4o-latest", "gpt-3.5-turbo", "o1-preview"]:
        os.environ["OPENAI_API_KEY"] = api_key
        embeddings = OpenAIEmbeddings(model=embedding_option)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Check if Chroma vector store already exists
    if os.path.exists(VECTORSTORE_DIR):
        vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
    else:
        os.makedirs(VECTORSTORE_DIR, exist_ok=True)
        os.makedirs(rag_data_dir, exist_ok=True)

        # Convert UTF-16 Volatility3 JSON files to UTF-8 and save to experimental RAG directory
        for file in os.listdir(volatility_data_dir):
            input_file = os.path.join(volatility_data_dir, file)
            output_file = os.path.join(rag_data_dir, file)

            if not os.path.exists(output_file):
                convert_utf16_to_utf8_json(input_file, output_file)

        # Load and process documents (PDFs and JSON files)
        documents = []
        for file in os.listdir(rag_data_dir):
            file_path = os.path.join(rag_data_dir, file)
            if file.endswith(".pdf"):
                pdf_loader = PyPDFLoader(file_path)
                documents.extend(pdf_loader.load())
            elif file.endswith(".json"):
                json_loader = JSONLoader(file_path=file_path, jq_schema=".[]", text_content=False)
                documents.extend(json_loader.load())

        # Split documents into smaller chunks
        split_docs = text_splitter.split_documents(documents)

        # Store document embeddings in Chroma vector store
        vectorstore = Chroma.from_documents(documents=split_docs, embedding=embeddings, persist_directory=VECTORSTORE_DIR)

    return vectorstore.as_retriever()
