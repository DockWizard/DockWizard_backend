from fastapi import APIRouter, Request
from starlette.responses import FileResponse

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    responses={404: {
        "description": "Not found"
    }},
)

# wget http://localhost:8000/assets/agent


@router.get("/agent")
async def get_agent_binary(request: Request):
    file_path = "assets/agent"
    return FileResponse(
        path=file_path,
        filename=file_path,
        media_type="application/octet-stream"
    )