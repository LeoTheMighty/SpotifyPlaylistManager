import spotipy
from spotify.oauth2 import SpotifyOAuth
from secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# Personal Designation for Liked Songs
LIKED_ID = None
LIKED_NAME = 'Liked Songs'

# Dictated by Spotify's API
MAX_ADD_ITEMS = 100
MAX_ADD_LIBRARY_ITEMS = 50
MAX_READ_ITEMS = 50
READ_SCOPE = "user-library-read"
MODIFY_PLAYLIST_SCOPE = "playlist-modify-public"
MODIFY_USER_LIBRARY_SCOPE = "user-library-modify"

def init_client(scope):
    """Instantiate a Spotify client with the given scope"""

    return spotipy.Spotify(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=scope)

def handle_all_from_pagination(handle, fetch, limit):
    """Process every item from a paginated API call.

    Args:
        handle ((dict) -> void): The function to handle each item retrieved from the actual API call.
        fetch ((offset: int, limit: int) -> ({ "items": [dict], "total": int )): The function to fetch the items from the API.
        limit (int): The limit for the number of items that can be fetched at once using the passed in fetch method.

    TODO: Maybe we could cache the fetch? Then we wouldn't have to worry about duplicated fetching.
    """

    offset = 0
    result = fetch(offset, limit)
    total = result['total']
    while offset != total:
        items = result['items']
        for item in items:
            handle(item)
        offset += len(items)
        result = fetch(offset, limit)

def batch_handle(items, handle_batch, limit):
    """Handles the batch logic for API calls that perform an operation on a batch of items that have a limit on how many items can be passed in.

    Args:
        items (list): The items to process into batches.
        handle_batch ((batch: list) -> void): The function to handle the batch'ed items.
        limit (int): The max number of items that the `handle_batch` function can take in.
    """
    while len(items) > 0:
        batch = items[:limit]
        handle_batch(batch)
        items = items[limit:]

class SpotifyHelper:
    """Helper class to handle all the logic to interact with the Spotify API"""

    def __init__(self):
        # init the clients
        self.sp_lib = init_client(READ_SCOPE)
        self.sp_pl_modify = init_client(MODIFY_PLAYLIST_SCOPE)
        self.sp_lib_modify = init_client(MODIFY_USER_LIBRARY_SCOPE)

    # Specific Spotify API actions
    # ============================
    def get_playlist_tracks(playlist_id):
        track_ids = set()

        # TODO: can you do a `lambda` with an `if`?
        def handle_track(track):
            if track['track']['id'] is not None:
                track_ids.add(track['track']['id'])

        # TODO does this work?
        handle_track = lambda track: track_ids.add(track['track']['id']) if track['track']['id'] is not None

        if playlist_id is LIKED:
            handle_liked_tracks(handle_track)
        else:
            handle_playlist_tracks(playlist_id, handle_track)
        return track_ids

    def get_track(track_id):
        self.sp_pl_modify(track_id)

    def update_playlist(playlist_id, track_ids):
        if playlist_id is LIKED:
            handle_batch(track_ids, lambda batch: self.sp_lib_modify.current_user_saved_tracks_add(batch), MAX_ADD_LIBRARY_ITEMS)
        else:
            handle_batch(track_ids, lambda batch: self.sp_pl_modify(playlist_id, batch), MAX_ADD_ITEMS)

    def get_track_names(track_ids):
        track_names = []

        def batch_handle(batch):
            for track in batch['tracks']:
                track_names.append("\"{}\" by {}".format(track['name'], SpotifyHelper.get_artists_string(track['artists'])))

        handle_batch(track_ids, batch_handle, MAX_READ_ITEMS)

        return track_names

    # Special handle methods
    # ============================
    def handle_all_playlists(handle_playlist):
        handle_all_from_pagination(handle_playlist, lambda offset, limit: self.sp_pl_modify.current_user_playlists(limit=limit, offset=offset), MAX_READ_ITEMS)

    def handle_playlist_tracks(playlist_id, handle_track):
        handle_all_from_pagination(handle_track, lambda offset, limit: self.sp_pl_modify.playlist_items(playlist_id, limit=limit, offset=offset), MAX_READ_ITEMS)

    def handle_liked_tracks(handle_track):
        handle_all_from_pagination(handle_track, lambda offset, limit: self.sp_lib.current_user_saved_tracks(limit=limit, offset=offset), MAX_READ_ITEMS)

    # Helper methods
    # ============================
    def self.get_artists_string(artists):
        # TODO: Do this functionally better with foldr or smth
        s = ""
        first = True
        for artist in artists:
            if not first:
                s += ", {}".format(artist['name'])
            else:
                s += artist['name']
                first = False
        return s

if __name__ == "__main__":
    # Run a test suite? Might be fun
    continue
