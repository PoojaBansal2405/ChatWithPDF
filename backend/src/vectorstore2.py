import os
import uuid
import chromadb
import numpy as np

from typing import List, Any, Optional

class VectorStore:

    def __init__(
            self,
            collection_name="pdf_documents",
            persist_directory="../data/vector_store"
    ):
        self.collection_name=collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            #Create persistent ChromaDB client 
            os.makedirs(self.persist_directory, exist_ok=True)
    
            self.client = chromadb.PersistentClient(path=self.persist_directory)
    
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name,
                metadata={"description":"PDF document embeddings for RAG",
                         "hnsw:space": "cosine"
                         }
             )
    
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing documents in collection {self.collection.count()}")
    
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[Any], embeddings: np.ndarray, document_id: Optional[str] = None, notebook_id: Optional[str] = None):
        """Add documents and their embeddings to the vector store
          
        Args:
             documents: List of langchain documents
             embeddings: Corresponding embeddings for the documents
        """
        
    
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        

        if len(documents) == 0:
            return

        if embeddings.shape[1] == 0:
            raise ValueError("Embedding dimension cannot be zero.")
    
        print(f"Adding {len(documents)} documents to vector store...")
    
          # Prepare data for chromaDB
    
        ids = []
        metadatas = []
        documents_text = []
      
        document_id = document_id or str(uuid.uuid4())

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
           
            chunk_id = f"{document_id}_{i}"
            
    
            # prepare metadata
            metadata = dict(doc.metadata)
             
            # Ensure ChromaDB-compatible metadata
            clean_metadata = {}

            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value

            clean_metadata["document_id"] = document_id
            clean_metadata["chunk_index"] = i

            if notebook_id is not None:
                clean_metadata["notebook_id"] = notebook_id
            ids.append(chunk_id)
            metadatas.append(clean_metadata)
            documents_text.append(doc.page_content)

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents_text
        )

        print(f"[INFO] Added {len(documents)} chunks.")
        print(f"[INFO] Total chunks: {self.collection.count()}")

        return document_id
            
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        notebook_id: Optional[str]=None
    ):
        """Search for similar document chunks."""

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self.collection.count() == 0:
            return []

        query_embedding = np.asarray(
            query_embedding, dtype="float32"
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.ndim != 2 or query_embedding.shape[0] != 1:
            raise ValueError("Query must contain exactly one embedding.")

        if notebook_id is not None:
            matching_count = len(self.collection.get(where={"notebook_id": notebook_id}, include=[])["ids"])
        else:
            matching_count = self.collection.count()

        if matching_count == 0:
            return []
        
        query_params = {
            "query_embeddings": query_embedding.tolist(),
            "n_results": min(top_k, matching_count),
            "include": ["documents", "metadatas", "distances"]
        }

        if notebook_id is not None:
            query_params["where"] = {
                "notebook_id": notebook_id
            }

        results = self.collection.query(
        **query_params
        )

        retrieved_docs = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        ids = results["ids"][0]

        for rank, (chunk_id, content, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances), start=1
        ):
            retrieved_docs.append({
                "id": chunk_id,
                "content": content,
                "metadata": metadata,
                "distance": float(distance),
                "similarity_score": 1 - float(distance),
                "rank": rank
            })

        return retrieved_docs

    def delete_document(self, document_id: str):
        """Delete all chunks belonging to a document."""

        self.collection.delete(
            where={"document_id": document_id}
        )

        print(f"[INFO] Deleted document: {document_id}")

    def count(self):
        """Return total number of stored chunks."""

        return self.collection.count()

    def get_all_documents(self):
        """Retrieve all stored chunks and metadata."""

        return self.collection.get(
            include=["documents", "metadatas"]
        )

    def delete_notebook(self, notebook_id: str):
        self.collection.delete(
            where={"notebook_id":notebook_id}
        )
