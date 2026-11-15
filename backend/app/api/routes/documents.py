from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.api.dependencies import get_document_service
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/notebooks/{notebook_id}/documents",
    tags=["Documents"]
)

@router.post("/upload")
async def upload_document(notebook_id: str, file: UploadFile = File(...), service: DocumentService = Depends(get_document_service)):
    """Upload a document to the knowledge base"""

    if not file.filename or not file.filename.strip():
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported."
        )

    try:
        content = await file.read(10*1024*1024+1)

        if len(content) > 10*1024*1024+1:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 10 MB limit"
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file."
            )

        document = await service.upload_document(filename=file.filename,content=content,notebook_id=notebook_id)

        return{
        "message": "Document uploaded successfully",
        "document": document
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        await file.close()
        

@router.get("/")
async def get_all_documents(notebook_id: str, service: DocumentService = Depends(get_document_service)):
    """Retrieve all uploaded documents"""
    documents = await service.get_all_documents(notebook_id=notebook_id)
    
    return{
        
        "documents": documents
    }

@router.get("/{document_id}")
async def get_document(notebook_id: str, document_id: str, service: DocumentService = Depends(get_document_service)):
    """
    Retrieve details of a specific document"""

    document = await service.get_document_by_id(notebook_id=notebook_id, document_id=document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    return document
    

@router.delete("/{document_id}")
async def delete_document(notebook_id:str, document_id: str , service: DocumentService = Depends(get_document_service)):
    """Delete a document from the knowledge base"""
    document = await service.delete_document(notebook_id, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
   
    return{
        "message": "Document deleted successfully",
    }