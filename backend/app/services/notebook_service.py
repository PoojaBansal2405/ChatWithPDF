import uuid
from datetime import datetime, timezone
import shutil
from pathlib import Path
from starlette.concurrency import run_in_threadpool

class NotebookService:

    def __init__(self, db):
        self.db = db
        self.collection = self.db["notebooks"]
        self.documents_collection = db["documents"]
        self.messages_collection = db["messages"]

    async def create_notebook(self, title: str):
        notebook_data = {
            "notebook_id": str(uuid.uuid4()),
            "title": title,
            "created_at": datetime.now(timezone.utc)
        }

        await self.collection.insert_one(notebook_data)

        return notebook_data

    async def get_all_notebooks(self):

        cursor = self.collection.find(
            {},
            {"_id": 0}
        )

        notebooks = await cursor.to_list(length=None)

        return notebooks

    async def get_notebook_by_id(self, notebook_id: str):
        notebook = await self.collection.find_one(
           {"notebook_id": notebook_id},
           {"_id": 0}
        )

        return notebook

    async def delete_notebook(self, notebook_id: str):
        notebook = await self.collection.find_one({"notebook_id": notebook_id})

        if notebook is None:
            return False

        # fetch all documents belonging to this notebook
        documents = await self.documents_collection.find({"notebook_id": notebook_id}).to_list(length=None)

        # delete all notebook chunks from chromadb
        await run_in_threadpool(
            self.vector_store.delete_notebook,
            notebook
        )

        #delete uploaded pdf folders
        uploads_root = Path("data/uploads").resolve()

        for document in documents:
            file_path = document.get("file_path")

            if not file_path:
                continue

            path = Path(file_path).resolve()
            folder = path.parent

            # only delete folders inside our uploads directory
            if uploads_root in folder.parents:
                await run_in_threadpool(
                    shutil.rmtree,
                    folder,
                    ignore_errors=True
                )

        await self.documents_collection.delete_many({"notebook_id":notebook_id})

        await self.messages_collection.delete_many({"notebook_id":notebook_id})

        result = await self.collection.delete_one({"notebook_id":notebook_id})

        return result.deleted_count > 0
    