
import uuid
from typing import Optional

from starlette.exceptions import HTTPException
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from app.shortcuts import (get_obj_or_404, 
    redirect, 
    render, 
    is_htmx)
from app.users.decorators import login_required
from app import utils
from app.videos.models import Video
from app.videos.schemas import VideoCreateSchema, VideoEditSchema
from app.watch_events.models import WatchEvent

router = APIRouter(
    prefix="/videos"
)



@router.get('/create', response_class=HTMLResponse)
@login_required
def video_create_view(request: Request, 
    playlist_id : Optional[uuid.UUID] =None,
    is_htmx=Depends(is_htmx)
    ):
    print(playlist_id)
    if is_htmx:
        return render(request, "videos/htmx/create.html", {})
    return render(request,"videos/create.html", {})


@router.post('/create', response_class=HTMLResponse)
@login_required
def video_create_post_view(request: Request, url:str = Form(...), title:str = Form(...),  is_htmx=Depends(is_htmx)): #To declare a field as required, you may declare it using just an annotation, or you may use an ellipsis (...) as the value
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

    if is_htmx:
        """
        Handle all HTMX requests
        """
        if len(errors) > 0:
            return render(request, "videos/create.html", context)
        context = {"path" : redirect_path, "title" : data.get('title')}
        return render(request, "videos/htmx/link.html", context)
    """
    Handle default HTML requests
    """
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
    start_time = 0 
    if request.user.is_authenticated:
        user_id = request.user.username
        start_time = WatchEvent.get_resume_time(host_id, user_id)
    context = {
        "host_id" : host_id,
        "start_time" : start_time,
        "object" : q
    }
    return render(request,"videos/detail.html", context)

@router.get('/{host_id}/edit', response_class=HTMLResponse)
@login_required
def video_edit_view(request: Request, host_id:str):
    q = get_obj_or_404(Video, host_id=host_id)
    
    context = {
        "object" : q
    }
    return render(request,"videos/edit.html", context)

@router.post('/{host_id}/edit', response_class=HTMLResponse)
@login_required
def video_edit_post_view(
    request: Request, 
    host_id : str,
    url:str = Form(...), 
    title:str = Form(...),  
    is_htmx=Depends(is_htmx)): #To declare a field as required, you may declare it using just an annotation, or you may use an ellipsis (...) as the value
    raw_data = {
        "title" : title,
        "url" : url,
        "user_id" : request.user.username
    }
    obj = get_obj_or_404(Video, host_id=host_id)
    data,errors = utils.valid_schema_data_or_error(raw_data, VideoEditSchema)
    
    if len(errors) > 0:
            return render(request, "videos/edit.html", context)

    obj.title = data.get('title') or obj.title
    obj.update_video_url(url, save=True)
    context ={
        "object" : obj
    }
    return render(request, "videos/edit.html", context)


@router.get('/{host_id}/hx-edit', response_class=HTMLResponse)
@login_required
def video_hx_edit_view(request: Request, host_id:str):
    if not is_htmx:
        raise HTTPException
    q = None
    not_found = False
    try:
        q = get_obj_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse("Not found, please try again.")
    context = {
        "object" : q
    }
    return render(request,"videos/htmx/edit.html", context)

@router.post('/{host_id}/hx-edit', response_class=HTMLResponse)
@login_required
def video_hx_edit_post_view(
    request: Request, 
    host_id : str,
    url:str = Form(...), 
    title:str = Form(...),  
    is_htmx=Depends(is_htmx),
    delete: Optional[bool] = Form(default=False)): #To declare a field as required, you may declare it using just an annotation, or you may use an ellipsis (...) as the value
    
    if not is_htmx:
        raise HTTPException
    obj = None
    not_found = False
    try:
        obj = get_obj_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse("Not found, please try again.")
    if delete:
        obj.delete()
        return HTMLResponse("Item Deleted")
    raw_data = {
        "title" : title,
        "url" : url,
        "user_id" : request.user.username
    }
    data,errors = utils.valid_schema_data_or_error(raw_data, VideoEditSchema)
    
    if len(errors) > 0:
            return render(request, "videos/htmx/edit.html", context)

    obj.title = data.get('title') or obj.title
    obj.update_video_url(url, save=True)
    context ={
        "object" : obj,
    }
    return render(request, "videos/htmx/list-inline.html", context)