from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_chat_service
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse, MessageResponse

router = APIRouter(
    prefix = "/notebooks/{notebook_id}/chat",
    tags=["Chat"]
)


## ask a question in a notebook
@router.post("/", response_model=ChatResponse)
async def ask_question(
notebook_id: str, 
request: ChatRequest, 
chat_service : ChatService = Depends(get_chat_service)
):
    try:
        result = await chat_service.ask_question(
        notebook_id=notebook_id,
        question=request.question
        )

        return result

    except ValueError as e:
        if str(e) == "Notebook not found.":
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[MessageResponse])
async def get_chat_history(
    notebook_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        return await chat_service.get_chat_history(notebook_id=notebook_id)
    except ValueError as e:
        if str(e) == "Notebook not found.":
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        