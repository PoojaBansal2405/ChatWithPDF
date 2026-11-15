
from typing import List, Any, Dict
from src.vectorstore2 import VectorStore
from src.embedding import EmbeddingPipeline

class RAGRetriever:
    """handles query based retrieval from vector store"""
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingPipeline):
        """Initialize the retriver
        
        Args:
            vector_store: Vector store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        """

        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query: str,  notebook_id: str, top_k: int = 5, score_threshold: float = 0.2) -> List[Dict[str,Any]]:
        """
        Retriever relevant documents for a query
        
        Args:
            query: The search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries containing retrieved documents and metadata
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if not notebook_id:
            raise ValueError("Notebook ID is required")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if not 0 <= score_threshold <= 1:
            raise ValueError("Score threshold must be between 0 and 1")

        
        print(f"Retriveing documents for query: '{query}'")
        print(f"Notebook ID:{notebook_id}")
        print(f"Top K: {top_k}, Score threshold: {score_threshold}")

        # Generate query embeddings
        query_embedding = self.embedding_manager.embed_query(query)

        ## Search in vector store
        try:
            results = self.vector_store.search(
                query_embedding=query_embedding,
                notebook_id=notebook_id,
                top_k=top_k
            )

            # Process results
            retrieved_docs = [doc for doc in results if doc["similarity_score"] >= score_threshold]

            print(f"Retrieved {len(retrieved_docs)} relevant chunks.")
            return retrieved_docs

        except Exception as e:
            print(f"Error during retrieval: {e}")
            raise




 