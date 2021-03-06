import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist,MultipleObjectsReturned

from app.config import get_settings
from app.users.exceptions import InvalidUserIDException
from app.videos.exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException
from app.videos.extractors import extract_video_id
from app.users.models import User
from app.shortcuts import templates

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
        return f"Video(title = {self.title}, host_id = {self.host_id}, host_service = {self.host_service})"
    
    def as_data(self):
        return {f"{self.host_service}_id" : self.host_id, "path" : self.path, "title": self.title}

    def render(self):
        base_name = self.host_service #youtube, vimeo
        template_name = f"videos/renderers/{base_name}.html"
        context = {"host_id" : self.host_id}
        t = templates.get_template(template_name)
        return t.render(context)

    @property
    def path(self):
        return f"/videos/{self.host_id}"

    def update_video_url(self, url, save=True):
        host_id = extract_video_id(url)
        if not host_id:
            return None
        self.host_id = host_id
        self.url = url
        if save:
            self.save()
        return url

    @staticmethod
    def get_or_create(url,user_id=None, **kwargs):
        host_id = extract_video_id(url)
        created = False
        obj = None
        try:
            obj = Video.objects.get(host_id=host_id)
        except MultipleObjectsReturned:
            q = Video.objects.allow_filtering().filter(host_id=host_id)
            obj = q.first()
        except DoesNotExist:
            obj = Video.add_video(url, user_id=user_id, **kwargs)
            created = True
        except:
            raise Exception("Invalid Request")
        return obj, created

    @staticmethod
    def add_video(url,user_id=None, **kwargs):
        # extract video_id from url
        # video_id = host_id
        # Service API - YouTube / Vimeo / etc
        host_id = extract_video_id(url)
        if host_id is None:
            raise InvalidYouTubeVideoURLException("Invalid Youtube Video URL")
        user_exist = User.check_exist(user_id)
        if user_exist is None:
            raise InvalidUserIDException("Invalid user_id")
        # user_obj = User.by_user_id(user_id)
        # user_obj.display_name
        q = Video.objects.allow_filtering().filter(host_id=host_id, user_id=user_id)
        if q.count() != 0:
            raise VideoAlreadyAddedException("Video Already added")
        return Video.create(host_id=host_id,user_id=user_id,url=url, **kwargs)