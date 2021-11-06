import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

SUPERLIST_INDICATOR = ' (personal)'

READ_SCOPE = "user-library-read"
MODIFY_PLAYLIST_SCOPE = "playlist-modify-public"

sp_library_read = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=READ_SCOPE))

sp_playlist_modify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=MODIFY_PLAYLIST_SCOPE))

def get_missing_tracks(playlist, sub_playlist):
    # Get all the tracks from playlist that are NOT currently in the sub-playlist
    return None

def add_tracks(playlist, tracks):
    sp_library_read.user_playlist_add_tracks(playlist, tracks)

if __name__ == "__main__":
    # user = sp_library_read.user('leothemighty123')
    saved_tracks = sp_library_read.current_user_saved_tracks()

    limit = 50
    playlists = sp_playlist_modify.current_user_playlists()
    playlist_name_map = {}
    offset = 0
    total = playlists['total']
    while offset != total:
        # print("Offset: ", end='')
        # print(offset, end=', ')
        # print("Total: ", end='')
        # print(total)
        items = playlists['items']
        # items.reverse()

        for playlist in items:
            name = playlist['name']
            personal_name = name + SUPERLIST_INDICATOR
            playlist_name_map[name] = playlist
            
            if personal_name in playlist_name_map:
                print(name + " is the sublist (ayo) of " + personal_name)
            if name.endswith(SUPERLIST_INDICATOR):
                # print(name + " is a personal list")
                real_name = name[:-len(SUPERLIST_INDICATOR)]
                if real_name in playlist_name_map:
                    print(real_name + " is the sublist of " + name)
            # print(playlist['name'], end=' ')
        
        offset += len(items)

        playlists = sp_playlist_modify.current_user_playlists(limit=limit, offset=offset)

    print("My Playlists ===>")
    print("Limit: ", end='')
    print(playlists['limit'])
    print("Next: ", end='')
    print(playlists['next'])
    print("Offset: ", end='')
    print(playlists['offset'])
    print("Previous: ", end='')
    print(playlists['previous'])
    print("Total: ", end='')
    print(playlists['total'])


    # for playlist in playlists['items']

    # print(sp_library_read.current_user())
    print(sp_playlist_modify.current_user_playlists()['total'])
    print(sp_library_read.current_user_saved_albums()['total'])
    print(sp_library_read.current_user_saved_tracks()['total'])
    print(sp_library_read.current_user_saved_tracks().keys())
    # print(user)

    # print

    # print(sp_library_read.current_user_playing_track())

