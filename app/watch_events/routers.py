from fastapi import APIRouter, Request
from .schemas import WatchEventSchema
from .models import WatchEvent

router = APIRouter()



@router.post('/api/events/watch', response_model = WatchEventSchema)
def watch_event_view(request : Request, watch_event : WatchEventSchema):
    
    if request.user.is_authenticated:
        cleaned_data = watch_event.dict()
        data = cleaned_data.copy()
        data.update({
            "user_id" : request.user.username
        }) 
        print(data)
        WatchEvent.objects.create(**data)
        return watch_event #or even cleaned_data can be returned
    return watch_event