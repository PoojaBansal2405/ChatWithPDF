import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.core.database import(connect_to_mongodb , 
close_mongodb_connection
)


from src.vectorstore2 import VectorStore
from src.embedding import EmbeddingPipeline
from src.retriever import RAGRetriever
from src.rag import AdvancedRAGPipeline

load_dotenv()

from app.api.routes.documents import router as documents_router
from app.api.routes.notebooks import router as notebooks_router
from app.api.routes.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Application startup
    await connect_to_mongodb(app)

    try:

        app.state.vector_store = VectorStore(
        collection_name="pdf_documents",
        persist_directory="../data/vector_store"
        )

        app.state.embedding_pipeline = EmbeddingPipeline()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("Groq_API_KEY is missing from .env")

        app.state.llm = ChatGroq(
            api_key=api_key,
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1024
        )

        app.state.rag_retriever = RAGRetriever(
            vector_store=app.state.vector_store,
            embedding_manager=app.state.embedding_pipeline
        )

        app.state.rag_pipeline = AdvancedRAGPipeline(
            retriever=app.state.rag_retriever,
            llm=app.state.llm
        )

        print("[INFO] RAG pipeline initialized successfully.")

        yield

    # Application shutdown
    finally:
        await close_mongodb_connection(app)

app = FastAPI(
    title="Chat with PDF",
    description="Your personal AI powered assistant",
    lifespan=lifespan
)

app.include_router(documents_router) 
app.include_router(notebooks_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message" : "Chat with PDF api is running!"}