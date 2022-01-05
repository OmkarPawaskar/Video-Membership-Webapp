from app import config
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


settings = config.get_settings()
templates = Jinja2Templates(directory= str(settings.templates_dir))

def render(request, template_name, context = {} , status_code: int = 200):
    ctx = context.copy()
    ctx.update({"request" : request})
    t = templates.get_template(template_name)
    html_str =  t.render(ctx)
    #set http only cookies
    responses = HTMLResponse(html_str, status_code = status_code)
    return responses
    #return templates.TemplateResponse(template_name, ctx)
