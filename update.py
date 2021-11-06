import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

SUPERLIST_INDICATOR = ' (personal)'

SPECIAL_SUBLISTS = {
    'LIKED': 'Cursed Combination'
}

READ_SCOPE = "user-library-read"
MODIFY_PLAYLIST_SCOPE = "playlist-modify-public"

MAX_ADD_ITEMS = 100

sp_library_read = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=READ_SCOPE))

sp_playlist_modify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=MODIFY_PLAYLIST_SCOPE))

def get_sublist_maps():
    sublist_map = {} # sublist to the superlist
    # basically get all the keys and make sure that their tracks are in their value (playlist)
    limit = 50
    playlists = sp_playlist_modify.current_user_playlists()
    playlist_name_map = {}
    offset = 0
    total = playlists['total']
    while offset != total:
        items = playlists['items']
        for playlist in items:
            name = playlist['name']
            personal_name = name + SUPERLIST_INDICATOR
            playlist_name_map[name] = playlist

            if personal_name in playlist_name_map:
                sublist_map[name] = personal_name
                # print(name + " is the sublist (ayo) of " + personal_name)
            if name.endswith(SUPERLIST_INDICATOR):
                # print(name + " is a personal list")
                real_name = name[:-len(SUPERLIST_INDICATOR)]
                if real_name in playlist_name_map:
                    sublist_map[real_name] = name
                    # print(real_name + " is the sublist of " + name)
            # print(playlist['name'], end=' ')

        offset += len(items)
        playlists = sp_playlist_modify.current_user_playlists(limit=limit, offset=offset)
    return sublist_map, playlist_name_map

def get_track_ids(playlist):
    playlist_id = playlist['id']
    limit = 50
    offset = 0
    tracks = sp_playlist_modify.playlist_items(playlist_id, limit=limit)
    total = tracks['total']
    track_ids = []
    while offset != total:

        for track in tracks['items']:
            # print(track['track'])
            # print(track['track']['name'])
            track_ids.append(track['track']['id'])

        offset += len(tracks['items'])
        tracks = sp_playlist_modify.playlist_items(playlist_id, limit=limit, offset=offset)
    return track_ids

def get_track_names(tracks):
    if len(tracks) == 0:
        return []
    elif len(tracks) > 50:
        return [x['name'] for x in sp_playlist_modify.tracks(tracks[0:50])['tracks']] + ['...']
    return [x['name'] for x in sp_playlist_modify.tracks(tracks)['tracks']] 

def get_missing_tracks(playlist, sub_playlist) -> list[dict]:
    # Get all the track ids from playlist that are NOT currently in the sub-playlist
    # SET operations, return sub_playlist - super_playslist
    sub_playlist_ids = set(get_track_ids(sub_playlist))
    playlist_ids = set(get_track_ids(playlist))
    # print("SUB = " + str(sub_playlist_ids))
    # print("PLAY = " + str(playlist_ids))
    return list(sub_playlist_ids - playlist_ids)

def update_playlist_from_sub(sub_playlist, playlist):
    missing_tracks = get_missing_tracks(playlist, sub_playlist)
    print("Adding " + str(get_track_names(missing_tracks)) + " (len = " + str(len(missing_tracks)) + ") to " + playlist['name'])
    if len(missing_tracks) != 0:
        while len(missing_tracks) > MAX_ADD_ITEMS:
            add_tracks = missing_tracks[0:MAX_ADD_ITEMS]
            missing_tracks = missing_tracks[MAX_ADD_ITEMS:]
            sp_playlist_modify.playlist_add_items(playlist['id'], add_tracks)
        sp_playlist_modify.playlist_add_items(playlist['id'], missing_tracks)
    

# def add_tracks(playlist, tracks):
    # sp_library_read.user_playlist_add_tracks(playlist, tracks)

if __name__ == "__main__":
    # user = sp_library_read.user('leothemighty123')
    saved_tracks = sp_library_read.current_user_saved_tracks()

    sublist_map, playlist_name_map = get_sublist_maps()
    # print(sublist_map)
    
    for k, v in sublist_map.items():
        # update_playlist_from_sub(playlist_name_map[k], playlist_name_map[v])
        # print(k + " is the sublist of " + v)
        print("UPDATING playlist [" + v + "] to have the tracks from sub_playlist [" + k + "]")
        update_playlist_from_sub(playlist_name_map[k], playlist_name_map[v])
        # if (k == "test"):
            # print("UPDATING subplaylist (" + k + ") to have the tracks from playlist (" + v + ")")
            # update_playlist_from_sub(playlist_name_map[k], playlist_name_map[v])
            # playlist = playlist_name_map[v]
            # sub_playlist = playlist_name_map[k]
            # missing_tracks = get_missing_tracks(playlist, sub_playlist)
            # print(missing_tracks)
            # print(sp_playlist_modify.tracks(missing_tracks))
            # print(get_track_names(missing_tracks))
            # sp_playlist_modify.playlist_add_items(playlist['id'], missing_tracks)

    # print("My Playlists ===>")
    # print("Limit: ", end='')
    # print(playlists['limit'])
    # print("Next: ", end='')
    # print(playlists['next'])
    # print("Offset: ", end='')
    # print(playlists['offset'])
    # print("Previous: ", end='')
    # print(playlists['previous'])
    # print("Total: ", end='')
    # print(playlists['total'])


    # for playlist in playlists['items']

    # print(sp_library_read.current_user())
    # print(sp_playlist_modify.current_user_playlists()['total'])
    # print(sp_library_read.current_user_saved_albums()['total'])
    # print(sp_library_read.current_user_saved_tracks()['total'])
    # print(sp_library_read.current_user_saved_tracks().keys())
    # print(user)

    # print

    # print(sp_library_read.current_user_playing_track())

