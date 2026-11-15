import shutil
import uuid

from pathlib import Path
from datetime import datetime, timezone

from starlette.concurrency import run_in_threadpool

from src.data_loader import load_single_document

class DocumentService:
    def __init__(self, db, vector_store, embedding_pipeline):
        self.db = db
        self.vector_store = vector_store
        self.embedding_pipeline = embedding_pipeline

        # MongoDB collection for document records
        self.collection = self.db["documents"]
        self.notebooks_collection = self.db["notebooks"]

        #directory for storing uploaded PDFs
        self.upload_dir = Path("data/uploads").resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)


    def _process_document(self, file_path: Path, document_id: str, notebook_id: str):
        """Load,chunk,embed and store a document"""

        #Load PDF
        documents = load_single_document(str(file_path))

        #split into chunks
        chunks = self.embedding_pipeline.chunk_documents(documents)

        if not chunks:
            raise ValueError("No chunks generated from the document.")

        # generate embeddings
        embeddings = self.embedding_pipeline.embed_chunks(chunks)

        # store chunks and embeddings in chromadb
        self.vector_store.add_documents(
            documents=chunks,
            embeddings=embeddings,
            document_id=document_id,
            notebook_id=notebook_id
        )
        return len(chunks)

    async def upload_document(self, filename: str, content: bytes, notebook_id: str):
        notebook = await self.notebooks_collection.find_one({"notebook_id": notebook_id})
        if notebook is None:
            raise ValueError("Notebook not found.")


        document_id = str(uuid.uuid4())

        # create a separate directory for this document
        document_dir = self.upload_dir / document_id
        document_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_filename = Path(filename.replace("\\", "/")).name
        file_path = document_dir / safe_filename

        try:
            # save the original pdf
            await run_in_threadpool(file_path.write_bytes, content)

            # process PDF 
            chunk_count = await run_in_threadpool(
            self._process_document,
            file_path,
            document_id,
            notebook_id
            )

            # prepare document metadata
            document_data = {
            "document_id": document_id,
            "notebook_id": notebook_id,
            "filename": safe_filename,
            "file_path": str(file_path),
            "chunk_count": chunk_count
            }

            # save metadata in mongodb
            await self.create_document_record(document_data)

            return document_data

        except Exception:
            #rollback 
            try:
                await run_in_threadpool(
                self.vector_store.delete_document,
                document_id
                )
            except Exception:
                pass

            #remove uploaded file and its directory
            await run_in_threadpool(
            shutil.rmtree,
            document_dir,
            ignore_errors=True
            )

            raise



        
    async def create_document_record(self, document_data: dict):
        """Save document info in MongoDB"""
        document_data["uploaded_at"] = datetime.now(timezone.utc)

        await self.collection.insert_one(document_data.copy())

        return document_data

    async def get_all_documents(self, notebook_id: str):
        """Retrieve all uploaded document records"""

        cursor = self.collection.find(
            {"notebook_id": notebook_id},
            {"_id": 0}
        )

        documents = await cursor.to_list(length=None)

        return documents

    async def get_document_by_id(self, document_id: str, notebook_id: str):
        """Retrieve a document using its id"""

        document = await self.collection.find_one(
        {"document_id": document_id,
         "notebook_id": notebook_id
        },
        {"_id":0}                             )

        return document

    async def delete_document(self, notebook_id:str , document_id: str):
        """delete a document and its associated chunks"""

        #first check whether the document exists
        document = await self.get_document_by_id(document_id= document_id, notebook_id= notebook_id)

        if document is None:
            return None

        # Delete associated chunks from ChromaDB
        await run_in_threadpool(
        self.vector_store.delete_document,
        document_id
        )

        # delete document record from mongodb
        await self.collection.delete_one(
            {"notebook_id": notebook_id,
            "document_id": document_id}
        )

        return document
