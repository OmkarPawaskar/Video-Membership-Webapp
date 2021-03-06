from fastapi import responses,Request
from app import config
from starlette.exceptions import HTTPException as StarletteHTTPException
from cassandra.cqlengine.query import DoesNotExist,MultipleObjectsReturned
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


settings = config.get_settings()
templates = Jinja2Templates(directory= str(settings.templates_dir))

def is_htmx(request : Request):
    return request.headers.get('hx-request') == "true"

def get_obj_or_404(ClassName, **kwargs):
    obj = None
    try:
        obj = ClassName.objects.get(**kwargs)
    except DoesNotExist:
        raise StarletteHTTPException(status_code=404)
    except MultipleObjectsReturned:
        raise StarletteHTTPException(status_code=400)
    except:
        raise StarletteHTTPException(status_code=500)
    return obj


def redirect(path, cookies:dict = {}, remove_session=False):
    response = RedirectResponse(path, status_code=302)
    for k,v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)
    if remove_session is True:
        response.set_cookie(key="session_ended", value=1, httponly=True)
        response.delete_cookie(key="session_id")
    return response

def render(request, template_name, context = {} , status_code: int = 200, cookies:dict = {}):
    ctx = context.copy()
    ctx.update({"request" : request})
    t = templates.get_template(template_name)
    html_str =  t.render(ctx)
    #set http only cookies
    response = HTMLResponse(html_str, status_code = status_code)
    #print(responses.cookies)
    response.set_cookie(key="darkmode", value=1)

    if len(cookies.keys()) > 0:
        #set http only cookies
        for k,v in cookies.items():
            response.set_cookie(key=k ,value=v ,httponly=True) #httponly arg ensures user is not able to edit via js console. ie as document.cookie
    
    #delete cookie
    #for key in cookies.keys():
    #    responses.delete_cookie(key)
    return response
    #return templates.TemplateResponse(template_name, ctx)
