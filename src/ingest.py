import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DATA_DIR = "data"
VECTORSTORE_DIR = "vectorstore"

def load_pdfs(data_dir: str):
    docs = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(data_dir, filename)
            print(f"Loading: {filename}")
            loader = PyMuPDFLoader(path)
            pages = loader.load()
            # Tag each chunk with source filename
            for page in pages:
                page.metadata["source_file"] = filename
            docs.extend(pages)
    print(f"Total pages loaded: {len(docs)}")
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,       # ~150 words per chunk — good for RAG
        chunk_overlap=100,    # overlap keeps context across chunks
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def embed_and_store(chunks):
    print("Loading embedding model (downloads once ~90MB)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        # Free, fast, good quality — 384 dimensions
    )
    print("Embedding and storing in ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    print(f"Done. Vectorstore saved to: {VECTORSTORE_DIR}/")
    return vectorstore

if __name__ == "__main__":
    docs   = load_pdfs(DATA_DIR)
    chunks = split_documents(docs)
    embed_and_store(chunks)
    print("\nIngestion complete. Run chatbot.py to start chatting.")