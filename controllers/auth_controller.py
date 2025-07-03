from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from db.models import User
from db.database import get_db
from sqlalchemy.orm import Session
import bcrypt
import uuid
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import RequestValidationError


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie("username")
    return response

@router.post("/", response_class=HTMLResponse)
def login_or_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    action: str = Form(...),
    db: Session = Depends(get_db)
):
    if action == "register":
        # Kiểm tra username/email đã tồn tại chưa
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Username hoặc email đã tồn tại!",
                "mode": "register"
            })
        # Kiểm tra độ dài mật khẩu
        if len(password) < 8:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Mật khẩu phải có ít nhất 8 ký tự!",
                "mode": "register"
            })
        # Hash password trước khi lưu
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username=username, password=hashed_pw, email=email, token="")
        db.add(user)
        db.commit()
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Đăng ký thành công, hãy đăng nhập!",
            "mode": "login"
        })
    else:  # action == "login"
        user = db.query(User).filter(User.username == username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Sinh token mới
            new_token = uuid.uuid4().hex
            user.token = new_token
            db.commit()
            response = RedirectResponse(url="/join", status_code=302)
            response.set_cookie(key="username", value=user.username)
            response.set_cookie(key="token", value=new_token)
            return response
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Sai tài khoản hoặc mật khẩu",
                "mode": "login"
            })


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("username")
    response.delete_cookie("token") 
    return response

