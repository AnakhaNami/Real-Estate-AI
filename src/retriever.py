import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from typing import List

VECTORSTORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vectorstore")

EMBEDDING_MODEL = None

def get_embeddings():
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        print("Loading embedding model...")
        EMBEDDING_MODEL = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return EMBEDDING_MODEL

def load_vectorstore():
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=get_embeddings()
    )

def hybrid_search(query: str, vectorstore, top_k: int = 5) -> List[Document]:
    # 1. Vector search
    vector_results = vectorstore.similarity_search(query, k=top_k * 2)

    if not vector_results:
        return []

    # 2. BM25 keyword re-rank on top of vector results
    corpus = [doc.page_content for doc in vector_results]
    tokenized = [doc.split() for doc in corpus]

    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.split())

    scored_docs = sorted(
        zip(scores, vector_results),
        key=lambda x: x[0],
        reverse=True
    )

    return [doc for _, doc in scored_docs[:top_k]]