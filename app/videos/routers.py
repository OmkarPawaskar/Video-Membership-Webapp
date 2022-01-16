from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from app.shortcuts import get_obj_or_404, redirect, render
from app.users.decorators import login_required
from app import utils
from app.videos.models import Video
from app.videos.schemas import VideoCreateSchema

router = APIRouter(
    prefix="/videos"
)

@router.get('/create', response_class=HTMLResponse)
@login_required
def video_create_view(request: Request):
    return render(request,"videos/create.html", {})


@router.post('/create', response_class=HTMLResponse)
@login_required
def video_create_view(request: Request, url:str = Form(...), title:str = Form(...)): #To declare a field as required, you may declare it using just an annotation, or you may use an ellipsis (...) as the value
    raw_data = {
        "title" : title,
        "url" : url,
        "user_id" : request.user.username
    }
    data,errors = utils.valid_schema_data_or_error(raw_data, VideoCreateSchema)
    redirect_path = data.get('path') or "/videos/create"
    context ={
        "data" : data,
        "errors" : errors,
        "title" : title,
        "url" : url,
    }

    if len(errors) > 0:
        return render(request, "videos/create.html", context, status_code=400)
    return redirect(redirect_path)

@router.get('/', response_class=HTMLResponse)
def video_list_view(request: Request):
    q = Video.objects.all().limit(100)
    context = {
        "object_list" : q
    }
    return render(request,"videos/list.html", context)

@router.get('/{host_id}', response_class=HTMLResponse)
def video_detail_view(request: Request, host_id:str):
    q = get_obj_or_404(Video, host_id=host_id)
    context = {
        "host_id" : host_id,
        "object" : q
    }
    return render(request,"videos/detail.html", context)