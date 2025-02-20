import os
import re
import asyncio
import platform
import langid
from bs4 import BeautifulSoup

from langchain_community.document_loaders import PyPDFLoader, AsyncHtmlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from utils.get_malpedia_references import get_references_from_malpedia

# Detect operating system
os_name = platform.system()

# Define appropriate directories based on OS
if os_name == "Windows":
    data_dir = "O:\\05_standard_rag"
else:  # Linux/macOS
    data_dir = "/tmp/MemoryInvestigator/05_standard_rag"

vectorstore_dir = os.path.join(data_dir, "chroma_store")

async def load_url_async(url):
    """
    Asynchronously loads an HTML document from a given URL, cleans it, removes irrelevant content,
    extracts metadata, and filters out non-English/German content.

    :param url: The URL to load.
    :return: The loaded HTML document.
    """
    try:
        loader = AsyncHtmlLoader(url)
        docs = await loader.aload()
        cleaned_docs = []

        for doc in docs:
            soup = BeautifulSoup(doc.page_content, "html.parser")

            # Remove unwanted HTML elements
            for tag in soup(["script", "style", "nav", "footer", "aside", "iframe", "noscript"]):
                tag.extract()

            # Remove common banners (GDPR, cookies, disclaimers)
            for banner in soup.find_all(text=re.compile(r"cookie|gdpr|privacy|terms|consent", re.IGNORECASE)):
                banner.extract()

            # Extract metadata
            title = soup.title.string if soup.title else ""
            if not title:
                h1 = soup.find("h1")
                title = h1.get_text(strip=True) if h1 else "Untitled"

            author_tag = soup.find("meta", attrs={"name": "author"}) or \
                         soup.find("meta", attrs={"property": "article:author"})
            author = author_tag["content"].strip() if author_tag and "content" in author_tag.attrs else "Unknown"

            date_tag = soup.find("meta", attrs={"property": "article:published_time"}) or \
                       soup.find("meta", attrs={"name": "datePublished"})
            published_date = date_tag["content"].strip() if date_tag and "content" in date_tag.attrs else "Unknown"

            # Extract and clean text
            text = soup.get_text(strip=True)

            # Detect Language using langid instead of langdetect
            detected_lang, _ = langid.classify(text)

            if detected_lang not in ["en", "de"]:
                print(f" Skipping {url} (Detected Language: {detected_lang})")
                continue  # Skip this document

            # Store valid document
            metadata = {
                "source": url,
                "title": title or "Untitled",
                "author": author or "Unknown",
                "published_date": published_date or "Unknown",
                "language": detected_lang
            }

            cleaned_docs.append(Document(page_content=text, metadata=metadata))

        return cleaned_docs

    except Exception as e:
        print(f"Error loading {url}: {e}")
        return []

async def load_all_urls(urls):
    """
    Asynchronously loads multiple URLs concurrently and cleans the content.

    :param urls: A list of URLs to fetch HTML content from.
    :return: A list of cleaned text documents or an empty list if an error occurs.
    """
    tasks = [load_url_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return [doc for sublist in results for doc in sublist]

def build_standard_rag(api_key, llm_option, embedding_option, malpedia_reference_name=None):
    """
    Builds a standard retrieval-augmented generation (RAG) model using uploaded PDFs.

    :param malpedia_reference_name: The Malpedia reference name (e.g., 'win.parite', or 'win.emotet') from https://malpedia.caad.fkie.fraunhofer.de/
    :param api_key: API key for LLM and Embeddings.
    :param llm_option: Selection if Google GenAI or OpenAI Model.
    :param embedding_option: Selection what embedding is chosen.
    :return: A retriever object for querying the generated vector store.
    """

    # Initialize embedding model
    if llm_option.startswith("gemini"):
        os.environ["GOOGLE_API_KEY"] = api_key
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_option)
    elif llm_option in ["gpt-4o", "gpt-3.5-turbo", "o1"]:
        os.environ["OPENAI_API_KEY"] = api_key
        embeddings = OpenAIEmbeddings(model=embedding_option)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # Check if Chroma vector store already exists
    if os.path.exists(vectorstore_dir):
        vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=embeddings)
    else:
        os.makedirs(vectorstore_dir, exist_ok=True)

        # Load and process PDF documents
        documents = []
        pdf_files = [file for file in os.listdir(data_dir) if file.endswith(".pdf")]
        if pdf_files:
            for file in pdf_files:
                pdf_loader = PyPDFLoader(os.path.join(data_dir, file))
                documents.extend(pdf_loader.load())

        # Fetch and load Malpedia references if enabled
        if malpedia_reference_name:
            urls = get_references_from_malpedia(malpedia_reference_name)
            documents.extend(asyncio.run(load_all_urls(urls)))

        # Split documents into smaller chunks
        split_docs = text_splitter.split_documents(documents)

        # Store document embeddings in Chroma vector store
        vectorstore = Chroma.from_documents(documents=split_docs, embedding=embeddings, persist_directory=vectorstore_dir)

    return vectorstore.as_retriever()
