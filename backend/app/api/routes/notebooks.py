from fastapi import APIRouter , Depends , HTTPException

from app.api.dependencies import get_notebook_service
from app.services.notebook_service import NotebookService
from app.schemas.notebook import NotebookCreate, NotebookResponse

router = APIRouter(
    prefix = "/notebooks",
    tags = ["Notebooks"]
)

@router.post("/", response_model=NotebookResponse)
async def create_notebook(notebook: NotebookCreate, service: NotebookService = Depends(get_notebook_service)):

    return await service.create_notebook(notebook.title)

@router.get("/", response_model=list[NotebookResponse])
async def get_all_notebooks(
    service: NotebookService = Depends(get_notebook_service)
):
    return await service.get_all_notebooks()
    

@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    service: NotebookService = Depends(get_notebook_service)
):
    notebook = await service.get_notebook_by_id(notebook_id)

    if notebook is None:
        raise HTTPException(
            status_code = 404,
            detail = "Notebook not found"
        )

    return notebook

@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: str,
    service: NotebookService = Depends(get_notebook_service)
):
    deleted = await service.delete_notebook(notebook_id)

    if not deleted:
        raise HTTPException(
            status_code = 404,
            detail = "Notebook not found"
        )

    return {"message": "Notebook deleted successfully"}





