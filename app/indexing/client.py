from ast import excepthandler
from algoliasearch.search_client import SearchClient
from app import config
from app.indexing.schemas import VideoIndexSchema,PlaylistIndexSchema
from app.videos.models import Video
from app.playlists.models import Playlist

settings = config.get_settings()

def get_index():
    client = SearchClient.create(
        settings.algolia_app_id,
        settings.algolia_api_key
    )
    index = client.init_index(settings.algolia_index_name)
    return index

def get_dataset():
    video_q = [dict(x) for x in Video.objects.all()]
    video_dataset = [VideoIndexSchema(**x).dict() for x in video_q]
    playlist_q = [dict(x) for x in Playlist.objects.all()]
    playlist_dataset = [PlaylistIndexSchema(**x).dict() for x in playlist_q]
    dataset = video_dataset + playlist_dataset
    return dataset

def update_index():
    index = get_index()
    dataset = get_dataset()
    idx_response = index.save_objects(dataset).wait()
    try:
        count = len(list(idx_response)[0]['objectIDs'])
    except:
        count = None
    return count

def search_index(query):
    index = get_index()
    return index.search(query)
