from datetime import datetime, timezone

from starlette.concurrency import run_in_threadpool

class ChatService:

    def __init__(self, db, rag_pipeline):
        self.db = db
        self.rag_pipeline = rag_pipeline

        self.messages_collection = self.db["messages"]
        self.notebooks_collection = self.db["notebooks"]

    async def ask_question(self, notebook_id: str, question: str):

        notebook = await self.notebooks_collection.find_one({"notebook_id": notebook_id})

        if notebook is None:
            raise ValueError("Notebook not found.")

        #store user's qiestion in mongoDB
        user_message = {
            "notebook_id": notebook_id,
            "role": "user",
            "content": question,
            "timestamp": datetime.now(timezone.utc)
        }

        await self.messages_collection.insert_one(user_message)

        #generate answer using rag_poipeline
        result = await run_in_threadpool(
            self.rag_pipeline.query,
            question=question,
            notebook_id=notebook_id,
            top_k=5,
            min_score=0.2,
            stream=False,
            summarize=False
        )

        answer = result["answer"]

        # store answer in mongodb
        assistant_message = {
            "notebook_id": notebook_id,
            "role":"assistant",
            "content":answer,
            "timestamp":datetime.now(timezone.utc)
        }
        await self.messages_collection.insert_one(assistant_message)

        return{
            "notebook_id": notebook_id,
            "question":question,
            "answer": answer
        }

    async def get_chat_history(self, notebook_id: str):
        notebook = await self.notebooks_collection.find_one(
            {"notebook_id": notebook_id}
        )

        if notebook is None:
            raise ValueError("Notebook not found")

        cursor = self.messages_collection.find({"notebook_id": notebook_id},
         {"_id":0 }                          
        ).sort("timestamp", 1)

        messages = await cursor.to_list(length=None)

        return messages



