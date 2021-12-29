import pathlib
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from cassandra.cqlengine.management import sync_table

from .users.models import User
from . import db

BASE_DIR = pathlib.Path(__file__).resolve().parent #app/
TEMPLATE_DIR = BASE_DIR / "templates"


app = FastAPI()
templates = Jinja2Templates(directory= str(TEMPLATE_DIR))

#settings = get_settings()
DB_SESSION = None


@app.on_event("startup")
def on_startup():
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(User)

@app.get('/', response_class=HTMLResponse)
def homepage(request : Request):
    context = {
        "request" : request,
        "abc" : "abc"
    }
    return templates.TemplateResponse("home.html", context)

@app.get('/login', response_class=HTMLResponse)
def login_get_view(request : Request):
    return templates.TemplateResponse("auth/login.html", {
        "request" : request
    })

@app.post('/login', response_class=HTMLResponse)
def login_get_view(request : Request,
    email : str = Form(...),
    password : str = Form(...)):
    print(email, password)
    return templates.TemplateResponse("auth/login.html", {
        "request" : request
    })


@app.get('/signup', response_class=HTMLResponse)
def signup_get_view(request : Request):
    return templates.TemplateResponse("auth/login.html", {
        "request" : request
    })

@app.post('/signup', response_class=HTMLResponse)
def signup_get_view(request : Request,
    email : str = Form(...),
    password : str = Form(...),
    password_confirm : str = Form(...)):
    print(email, password, password_confirm)
    return templates.TemplateResponse("auth/login.html", {
        "request" : request
    })


@app.get('/users')
def users_list_view():
    q = User.objects.all().limit(10)
    return list(q)