from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from controllers.auth_controller import router as auth_router
from controllers.chat_controller import router as chat_router
from utils.connection_manager import ConnectionManager
connection_manager = ConnectionManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(chat_router)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        # Trả về trang login với thông báo hết phiên
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Phiên đăng nhập đã hết, vui lòng đăng nhập lại!",
                "mode": "login"
            },
            status_code=401
        )
    # Các lỗi khác giữ nguyên
    return await fastapi.exception_handlers.http_exception_handler(request, exc)