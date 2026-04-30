"""FAISS vector store management for the Alfred chatbot."""

import hashlib
import logging
import math
import re
from typing import List, Dict

from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_PROVIDER,
    FAISS_INDEX_PATH,
    LOCAL_EMBEDDING_DIMENSIONS,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_API_KEY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalHashEmbeddings(Embeddings):
    """Small dependency-free local embeddings for FAISS keyword retrieval."""

    def __init__(self, dimensions: int = LOCAL_EMBEDDING_DIMENSIONS):
        self.dimensions = dimensions

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector


class VectorStoreManager:
    """Manages FAISS vector store for document retrieval."""
    
    def __init__(self, index_path=FAISS_INDEX_PATH):
        self.index_path = index_path
        self.embeddings = self._create_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self.vector_store = None

    def _create_embeddings(self):
        """Create embeddings for FAISS using local or OpenAI provider."""
        if EMBEDDING_PROVIDER == "openai":
            if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
                raise ValueError("OPENAI_API_KEY is missing. Add it to .env or use EMBEDDING_PROVIDER=local.")
            return OpenAIEmbeddings(
                model=OPENAI_EMBEDDING_MODEL,
                openai_api_key=OPENAI_API_KEY,
            )

        logger.info("Using dependency-free local hash embeddings for FAISS")
        return LocalHashEmbeddings()
    
    def create_from_documents(self, documents: List[Dict[str, str]]) -> FAISS:
        """
        Create FAISS index from scraped documents.
        
        Args:
            documents: List of document dictionaries with 'content' key.
            
        Returns:
            FAISS vector store instance.
        """
        logger.info("Creating vector store from documents...")
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc["content"])
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    "url": doc.get("url", ""),
                    "title": doc.get("title", ""),
                    "source": doc.get("source", "")
                })
        
        if not texts:
            raise ValueError("No text chunks were created from scraped documents.")
        
        logger.info("Created %s text chunks", len(texts))
        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        # Save to disk
        self.save()
        
        logger.info("Vector store created and saved to %s", self.index_path)
        return self.vector_store
    
    def load(self) -> FAISS:
        """
        Load existing FAISS index from disk.
        
        Returns:
            FAISS vector store instance or None if not found.
        """
        if self.index_path.exists():
            self.vector_store = FAISS.load_local(
                str(self.index_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Loaded existing vector store from %s", self.index_path)
            return self.vector_store
        
        logger.warning("No existing vector store found at %s", self.index_path)
        return None
    
    def save(self) -> None:
        """Save vector store to disk."""
        if self.vector_store:
            self.index_path.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(self.index_path))
            logger.info("Vector store saved to %s", self.index_path)
    
    def get_retriever(self, k: int = 4):
        """
        Get a retriever from the vector store.
        
        Args:
            k: Number of documents to retrieve.
            
        Returns:
            Retriever instance.
        """
        if not self.vector_store:
            self.load()
        
        if self.vector_store:
            return self.vector_store.as_retriever(search_kwargs={"k": k})
        
        return None


def create_vector_store(documents: List[Dict[str, str]]) -> FAISS:
    """
    Convenience function to create vector store.
    
    Args:
        documents: List of document dictionaries.
        
    Returns:
        FAISS vector store instance.
    """
    manager = VectorStoreManager()
    return manager.create_from_documents(documents)


def load_vector_store() -> FAISS:
    """
    Convenience function to load existing vector store.
    
    Returns:
        FAISS vector store instance or None.
    """
    manager = VectorStoreManager()
    return manager.load()


if __name__ == "__main__":
    # Test vector store creation
    from src.scraper import scrape_company_data
    
    print("Scraping company data...")
    docs = scrape_company_data()
    
    print("\nCreating vector store...")
    vs = create_vector_store(docs)
    print("Vector store created successfully!")
