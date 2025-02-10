import os

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

from utils.get_malpedia_references import get_references_from_malpedia


def build_standard_rag(api_key, llm_option, embedding_option, malpedia_reference_name=None):
    """
    Builds a standard retrieval-augmented generation (RAG) model using uploaded PDFs.

    :param malpedia_reference_name: The Malpedia reference name (e.g., 'win.parite', or 'win.emotet') from https://malpedia.caad.fkie.fraunhofer.de/
    :param api_key: API key for LLM and Embeddings.
    :param llm_option: Selection if Google GenAI or OpenAI Model.
    :param embedding_option: Selection what embedding is chosen.
    :return: A retriever object for querying the generated vector store.
    """

    # Define data directories
    data_dir = "O:\\05_standard_rag"
    vectorstore_dir = "O:\\05_standard_rag\\chroma_store"

    # Initialize embedding model
    if llm_option.startswith("gemini"):
        # Google GenAI Model
        os.environ["GOOGLE_API_KEY"] = api_key
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_option)
    elif llm_option == "chatgpt-4o-latest" or llm_option == "gpt-3.5-turbo" or llm_option == "o1-preview":
        # OpenAI Model
        os.environ["OPENAI_API_KEY"] = api_key
        embeddings = OpenAIEmbeddings(model=embedding_option)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Check if Chroma vector store already exists
    if os.path.exists(vectorstore_dir):
        vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=embeddings)
    else:
        os.makedirs(vectorstore_dir)

        # Load and process PDF documents
        documents = []
        pdf_files = [file for file in os.listdir(data_dir) if file.endswith(".pdf")]
        if pdf_files:  # Check if there are PDF files in the directory
            for file in pdf_files:
                pdf_loader = PyPDFLoader(os.path.join(data_dir, file))
                documents.extend(pdf_loader.load())

        # Fetch and load Malpedia references if enabled
        if malpedia_reference_name is not None :
            urls = get_references_from_malpedia(malpedia_reference_name)
            for url in urls:
                try:
                    web_loader = WebBaseLoader(url)
                    documents.extend(web_loader.load())
                except Exception as e:
                    print(f"Error loading Malpedia reference from {url}: {e}")

        # Split documents into smaller chunks
        split_docs = text_splitter.split_documents(documents)

        # Store document embeddings in Chroma vector store
        vectorstore = Chroma.from_documents(documents=split_docs, embedding=embeddings, persist_directory=vectorstore_dir)

    return vectorstore.as_retriever()