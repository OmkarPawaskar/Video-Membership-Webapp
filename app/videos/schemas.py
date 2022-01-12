import uuid
from pydantic import (
    BaseModel,
    validator,
    root_validator
)
from app.users.exceptions import InvalidUserIDException
from app.videos.exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException
from .extractors import extract_video_id
from .models import Video

class VideoCreateSchema(BaseModel):
    url : str #user generated
    title : str #user generated
    user_id : uuid.UUID  #request.session user

    @validator('url')
    def validate_youtube_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f'{url} is not a valid Youtube URL')
        return video_id

    @root_validator
    def validate_data(cls, values):
        url = values.get('url')
        user_id = values.get('user_id')
        video_obj = None
        try:
            video_obj = Video.add_video(url, user_id=user_id)
        except InvalidYouTubeVideoURLException:
            raise ValueError(f"{url} is not a valid Youtube URL")
        except VideoAlreadyAddedException:
            raise ValueError(f"{url} was already added to your account.")
        except InvalidUserIDException:
            raise ValueError("There was a problem with your account. Please try again!")
        except :
            raise ValueError("There was a problem with your account. Please try again!")
        if video_obj is None:
            raise ValueError("There was a problem with your account. Please try again!")
        if not isinstance(Video, video_obj):
            raise ValueError("There was a problem with your account. Please try again!")
        return video_obj.as_data()