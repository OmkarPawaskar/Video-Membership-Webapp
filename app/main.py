import pathlib
from fastapi import FastAPI, Request
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

@app.get('/users')
def users_list_view():
    q = User.objects.all().limit(10)
    return list(q)