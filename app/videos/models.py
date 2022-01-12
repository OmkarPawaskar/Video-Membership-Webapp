import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app.config import get_settings
from app.users.exceptions import InvalidUserIDException
from app.videos.exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException
from app.videos.extractors import extract_video_id
from app.users.models import User

settings = get_settings()

class Video(Model):

    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key = True) #Youtube,DailyMotion
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    host_service = columns.Text(default="youtube")
    title = columns.Text()
    url = columns.Text() #secure
    user_id = columns.UUID()


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Video(title = {self.title}, host_id = {self.host_id}, host_service = {self.host_service}"

    @staticmethod
    def add_video(url,user_id=None):
        # extract video_id from url
        # video_id = host_id
        # Service API - YouTube / Vimeo / etc
        host_id = extract_video_id(url)
        if host_id is None:
            raise InvalidYouTubeVideoURLException()
        user_exist = User.check_exist(user_id)
        if user_exist is None:
            raise InvalidUserIDException()
        # user_obj = User.by_user_id(user_id)
        # user_obj.display_name
        q = Video.objects.allow_filtering().filter(host_id=host_id, user_id=user_id)
        if q.count() != 0:
            raise VideoAlreadyAddedException()
        return Video.create(host_id=host_id,user_id=user_id,url=url)