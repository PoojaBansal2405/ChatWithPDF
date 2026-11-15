from fastapi import Request

from app.services.document_service import DocumentService
from app.services.notebook_service import NotebookService
from app.services.chat_service import ChatService

def get_document_service(request: Request):
    db = request.app.state.db
    vector_store = request.app.state.vector_store
    embedding_pipeline=request.app.state.embedding_pipeline

    return DocumentService(
        db = db,
        vector_store = vector_store,
        embedding_pipeline=embedding_pipeline
    )

def get_notebook_service(request: Request):
    db = request.app.state.db
    vector_store = request.app.state.vector_store
    return NotebookService(
        db = db,
        vector_store=vector_store
    )

def get_chat_service(request: Request):
    db=request.app.state.db
    rag_pipeline=request.app.state.rag_pipeline

    return ChatService(
      db=db,
      rag_pipeline=rag_pipeline
    )
