from fastapi import responses
from app import config
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


settings = config.get_settings()
templates = Jinja2Templates(directory= str(settings.templates_dir))

def redirect(path, cookies:dict = {}):
    response = RedirectResponse(path, status_code=302)
    for k,v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)
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
            response.set_cookie(key=k ,value=v ,httponly=True) #httponly arg ensures user is not able to edit via js console.
    
    #delete cookie
    #for key in cookies.keys():
    #    responses.delete_cookie(key)
    return response
    #return templates.TemplateResponse(template_name, ctx)
