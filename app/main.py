from distutils.log import debug
import io
import pathlib
import uuid
from functools import lru_cache
from wsgiref.util import setup_testing_defaults
from click import echo
from fastapi import (
    FastAPI,
    Depends,
    Request,
    File,
    UploadFile,
    HTTPException,
)
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "OCR Mirco service"
    debug: bool = False
    echo_active: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
DEBUG = settings.debug

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.post("/")
def home_view():
    return {"This is a POST": "request"}

@app.post("/img-echo/", response_class=FileResponse) #http post
async def image_echo_view(file: UploadFile = File(...), settings:Settings = Depends(get_settings)):
    if settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)
    UPLOAD_DIR.mkdir(exist_ok=True) # makes the dir in case of absence
    bytes_str = io.BytesIO(await file.read())
    # dest = UPLOAD_DIR / file.filname # can't save files with same name over and over with this way
    fname = pathlib.Path(file.filename)
    fext = fname.suffix # file extension i.e .jpg .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    with open(str(dest), "wb") as out:
        out.write(bytes_str.read())
    return dest
