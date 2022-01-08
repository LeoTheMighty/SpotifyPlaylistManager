import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

"""
1. Adds all the regular playlist ids to the (personal) corresponding playlist
2. Adds every playlist track to Liked
3. Adds every Liked song to Cursed Combination
4. Adds every we ____ song to My Recommended Songs
5. Maintain archive playlists that remove the songs in them from their corresponding playlists
"""

# If this is a part of the name, then it'll be a superlist to the normal one
SUPERLIST_INDICATOR = ' (personal)'

# TODO
ARCHIVE_INDICATOR = ' (archived)'

# I use the '*' character in my playlists to indicate special cases, but
# that's irrelevant for this script so we'll just remove them all.
IGNORE_CHARACTER = '*'

# I'll ignore case when calculating these anyways
ADD_TO_RECOMMENDED_PREFIXES = ['we']

# Recommended Playlist is a special one
RECOMMENDED_PLAYLIST_NAME = 'My Recommended Songs'
# TODO
RECOMMENDED_ARCHIVE_PLAYLIST_NAME = 'My Archived Recommended Songs'

# All the songs in my liked should be in these playlists (usually shared playlists)
UPDATE_WITH_LIKED = ['Cursed Combination']

# dictated by Spotify's API
MAX_ADD_ITEMS = 100

# different for saving songs for some reason?
MAX_ADD_LIBRARY_ITEMS = 50

READ_SCOPE = "user-library-read"
sp_library_read = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=READ_SCOPE))

MODIFY_PLAYLIST_SCOPE = "playlist-modify-public"
sp_playlist_modify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=MODIFY_PLAYLIST_SCOPE))

MODIFY_USER_LIBRARY_SCOPE = 'user-library-modify'
sp_user_library_modify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                       client_secret=CLIENT_SECRET,
                                                       redirect_uri=REDIRECT_URI,
                                                       scope=MODIFY_USER_LIBRARY_SCOPE))

def should_add_to_recommended(playlist_name):
    """Calculates whether the playlist should be added to the Recommended playlist.

    Args:
        playlist_name (str): The name of the playlist

    Returns:
        bool: Whether the playlist should be added to the Recommended playlist.
    """
    for p in ADD_TO_RECOMMENDED_PREFIXES:
        if playlist_name.replace(IGNORE_CHARACTER, '').lower().startswith(p):
            return True
    return False

def process_all_playlists(process_playlist):
    """Hands over each playlist over to the given function
    """
    limit = 50
    offset = 0
    playlists = sp_playlist_modify.current_user_playlists()
    total = playlists['total']
    while offset != total:
        items = playlists['items']
        for playlist in items:
            process_playlist(playlist)
        offset += len(items)
        playlists = sp_playlist_modify.current_user_playlists(limit=limit, offset=offset)

def get_from_list_map(d, k):
    """
    """
    if k not in d:
        return []
    return d[k]

def add_to_list_map(d, k, v):
    """
    """
    if k not in d.keys():
        d[k] = []
    d[k].append(v)

def get_playlists_info():
    """Gets all the necessary playlist info for the user.
    """
    playlist_names = {}
    playlist_name_map = {}
    playlist_superlists = {}
    add_to_recommended_playlist_names = []

    def add_superlist(sub_playlist_name, super_playlist_name):
        """Add to

        """
        for sub_playlist_id in get_from_list_map(playlist_name_map, sub_playlist_name):
            for super_playlist_id in get_from_list_map(playlist_name_map, super_playlist_name):
                add_to_list_map(playlist_superlists, sub_playlist_id, super_playlist_id)

    def handle_playlist(playlist):
        """
        """
        playlist_id = playlist['id']
        playlist_name = playlist['name']

        if should_add_to_recommended(playlist_name):
            add_to_recommended_playlist_names.append(playlist_name)

        playlist_names[playlist_id] = playlist_name
        add_to_list_map(playlist_name_map, playlist_name, playlist_id)

        personal_name = playlist_name + SUPERLIST_INDICATOR
        if personal_name in playlist_name_map:
            add_superlist(playlist_name, personal_name)
            # print(name + " is the sublist (ayo) of " + personal_name)
        if playlist_name.endswith(SUPERLIST_INDICATOR):
            # print(name + " is a personal list")
            real_name = playlist_name[:-len(SUPERLIST_INDICATOR)]
            if real_name in playlist_name_map:
                add_superlist(real_name, playlist_name)

    process_all_playlists(handle_playlist)

    for playlist_name in add_to_recommended_playlist_names:
        add_superlist(playlist_name, RECOMMENDED_PLAYLIST_NAME)

    # playlists = { "id": "name" }
    # playlist_name_map = { "name": ["ids", "with", "that", "name"] }
    # playlist_superlists = { "sub_playlist_id": ["list", "of", "super_playlists", "to_update"] }
    return playlist_names, playlist_name_map, playlist_superlists

def get_ids(get_tracks):
    """Gets the track ids from a playlist given a function that grabs the track objects.

    Args:
        get_tracks ((limit, offset) -> [Track]): Function to get tracks given a limit and offset.

    Returns:
        set(str): The list of ids representing the tracks from the function.
    """
    limit = 50
    offset = 0
    tracks = get_tracks(limit, offset)
    total = tracks['total']
    track_ids = set()
    while offset != total:
        for track in tracks['items']:
            # These are local files in my playlists, we don't want to process them
            if track['track']['id'] is not None:
                track_ids.add(track['track']['id'])
        offset += len(tracks['items'])
        tracks = get_tracks(limit, offset)
    return track_ids

def get_liked_tracks():
    """Get the list of ids

    """
    return get_ids(lambda limit, offset: sp_library_read.current_user_saved_tracks(limit=limit, offset=offset))

def get_playlist_tracks(playlist_id):
    """
    """
    return get_ids(lambda limit, offset: sp_playlist_modify.playlist_items(playlist_id, limit=limit, offset=offset))

def get_all_playlist_tracks(playlist_names):
    """
    id -> set(track_ids)
    """
    print("[DEBUG] Getting the sets of playlist tracks:")
    print("[DEBUG]  ")
    playlist_tracks = {}
    for playlist_id, playlist_name in playlist_names.items():
        tracks = get_playlist_tracks(playlist_id)
        print("[DEBUG]  \"{}\" has {} tracks".format(playlist_name, len(tracks)))
        playlist_tracks[playlist_id] = tracks

    print("[DEBUG]  =====================================")
    print("[DEBUG]  Calculated for {} playlists".format(len(playlist_tracks.keys())))
    print("[DEBUG]  =====================================")
    return playlist_tracks

def add_to_liked(track_ids):
    """
    """
    print("Adding " + str(get_track_names(track_ids)) + " (len = " + str(len(track_dis)) + ") to Liked")
    if len(track_ids) != 0:
        while len(track_ids) > MAX_ADD_ITEMS:
            add_tracks = track_ids[0:MAX_ADD_ITEMS]
            track_ids = track_ids[MAX_ADD_ITEMS:]
            sp_playlist_modify.current_user_saved_tracks_add(add_tracks)
        sp_playlist_modify.current_user_saved_tracks_add(add_tracks)

def get_track(track_id):
    return sp_playlist_modify.track(track_id)

def pretend_its_an_offsetted_api_call_i_guess(track_ids, limit, offset):
    track_ids = track_ids[offset:offset+limit]
    if len(track_ids) == 0:
        return []
    return sp_playlist_modify.tracks(track_ids)

def get_artists_string(artists):
    # prolly could do this functionally but whatever
    s = ""
    first = True
    for artist in artists:
        if not first:
            s += ", {}".format(artist['name'])
        else:
            s += artist['name']
            first = False
    return s

def get_track_names(track_ids):
    """
    """
    limit = 50
    offset = 0
    total = len(track_ids)
    track_ids = list(track_ids)
    tracks = pretend_its_an_offsetted_api_call_i_guess(track_ids, limit, offset)
    track_names = []
    while offset != total:
        for track in tracks['tracks']:
            track_names.append("\"{}\" by {}".format(track['name'], get_artists_string(track['artists'])))
        offset += len(tracks['tracks'])
        tracks = pretend_its_an_offsetted_api_call_i_guess(track_ids, limit, offset)
    return track_names

def get_missing_tracks(sub_playlist_tracks, super_playlist_tracks):
    """Get the tracks that need to get added to the super playlist. Simple Set subtraction.

    Args:
        sub_playlist_tracks (set[str]): The set of track ids for the sub playlist
        super_playlist_tracks (set[str]): The set of track ids for the super playlist

    Returns:
        set[str]: The set of track ids missing from the super playlist.
    """
    return sub_playlist_tracks - super_playlist_tracks

def get_playlists_to_update(playlist_superlists, playlist_tracks, playlist_names):
    """

    Returns:
        dict[str, set(str)]: Map of playlist ID to the set of track ids to add.
    """
    print("[DEBUG] Getting the playlists to update:")
    print("[DEBUG]  ")
    playlists_to_update = {}
    for sublist, superlists in playlist_superlists.items():
        for superlist in superlists:
            sublist_tracks = playlist_tracks[sublist]
            superlist_tracks = playlist_tracks[superlist]
            missing_tracks = get_missing_tracks(sublist_tracks, superlist_tracks)

            # Ensure that we don't have any empty updates in the map at all
            if len(missing_tracks) != 0:
                print("[DEBUG]  \"{}\" is missing {} tracks FROM sublist \"{}\"".format(playlist_names[superlist], len(missing_tracks), playlist_names[sublist]))
                if superlist not in playlists_to_update:
                    playlists_to_update[superlist] = set()
                playlists_to_update[superlist].update(missing_tracks)

    print("[DEBUG]  =====================================")
    print("[DEBUG]  There are {} playlists to update".format(len(playlists_to_update.keys())))
    print("[DEBUG]  =====================================")

    return playlists_to_update

def get_missing_liked_tracks(liked_tracks, playlist_names, playlist_tracks):
    """
    """
    total_missing_tracks = set()
    for playlist_id, track_ids in playlist_tracks.items():
        missing_tracks = get_missing_tracks(track_ids, liked_tracks)
        if len(missing_tracks) != 0:
            total_missing_tracks.update(missing_tracks)
    return total_missing_tracks

def update_liked_songs(track_ids):
    """
    """
    while len(track_ids) > 0:
        add_tracks = track_ids[:MAX_ADD_LIBRARY_ITEMS]
        sp_user_library_modify.current_user_saved_tracks_add(add_tracks)
        track_ids = track_ids[MAX_ADD_LIBRARY_ITEMS:]

def update_playlist(playlist_id, track_ids):
    """
    """
    while len(track_ids) > 0:
        add_tracks = track_ids[:MAX_ADD_ITEMS]
        sp_playlist_modify.playlist_add_items(playlist_id, add_tracks)
        track_ids = track_ids[MAX_ADD_ITEMS:]

def update_playlists(playlists_to_update, missing_liked_tracks):
    """
    """
    num_updated = 0
    for playlist, track_ids in playlists_to_update.items():
        update_playlist(playlist, list(track_ids))
        num_updated += len(track_ids)
    update_liked_songs(list(missing_liked_tracks))
    num_updated += len(missing_liked_tracks)
    return num_updated

def print_accomplish_plan():
    """
    """
    print("================================")
    print("What this script will do:")
    print()
    print("1. It will use the SUPERLIST_INDICATOR = \"{}\" to figure out what playlists are sub-playlists of others.".format(SUPERLIST_INDICATOR))
    print("      For instance in your case: \"My Cool Playlist\" is a sublist of \"My Cool Playlist{}\"".format(SUPERLIST_INDICATOR))
    print("2. It will add all of your playlists over to your Liked Songs automatically.")
    print("3. It will add every Liked Song to these playlists: {}".format(UPDATE_WITH_LIKED))
    print("4. It will add every song from the playlists with these prefixes: {} to your general Recommended Playlist named \"{}\"".format(ADD_TO_RECOMMENDED_PREFIXES, RECOMMENDED_PLAYLIST_NAME))
    # TODO
    # print("5. It will maintain an Archived Recommended playlist named \"{}\" where the items in this list are removed from the Recommended playlist".format(RECOMMENDED_ARCHIVE_PLAYLIST_NAME))
    print()

def print_playlist_plan(playlist_names, playlist_name_map, playlist_superlists):
    """Print the plan that we want to do to update the library.
    """
    print("================================")
    print("Playlist update plan:")
    print()
    for sublist, superlists in playlist_superlists.items():
        for superlist in superlists:
            print("{} -> {}".format(playlist_names[sublist], playlist_names[superlist]))
    for k, v in playlist_name_map.items():
        if len(v) == 1:
            print("{} -> Liked".format(k))
        else:
            for i in v:
                print("{} (id: {}) -> Liked".format(k, i))
    print()

def print_detailed_track_plan(playlists_to_update, missing_liked_tracks, playlist_names):
    """
    """
    print("================================")
    print("What will get updated:")
    print()
    for playlist, tracks in playlists_to_update.items():
        print("\"{}\" (to add {} tracks):".format(playlist_names[playlist], len(tracks)))
        for i, track_name in enumerate(get_track_names(tracks)):
            print("    {}. {}".format(i, track_name))
        print()
    print("~Liked Songs~ (to add {} tracks):".format(len(missing_liked_tracks)))
    for i, track_name in enumerate(get_track_names(missing_liked_tracks)):
        print("    {}. {}".format(i, track_name))
    print()

def main():
    print_accomplish_plan()

    playlist_names, playlist_name_map, playlist_superlists = get_playlists_info()

    # print_playlist_plan(playlist_names, playlist_name_map, playlist_superlists)

    liked_tracks = get_liked_tracks()

    print("[DEBUG] You have {} Liked Songs".format(len(liked_tracks)))
    print("[DEBUG]  ")

    playlist_tracks = get_all_playlist_tracks(playlist_names)

    missing_liked_tracks = get_missing_liked_tracks(liked_tracks, playlist_names, playlist_tracks)
    playlists_to_update = get_playlists_to_update(playlist_superlists, playlist_tracks, playlist_names)

    print_detailed_track_plan(playlists_to_update, missing_liked_tracks, playlist_names)

    print()
    print("Look at the track update plan and make sure it's what you want!!")
    print()
    print("If you're ready to proceed, type \"YES\" to update your library. Anything else will cancel")
    answer = input()
    if answer != "YES":
        print("Aborting...")
        return

    # print("haha jk it's not implemented yet")

    num_updated = update_playlists(playlists_to_update, missing_liked_tracks)
    print("Successfully added {} tracks to different playlists in your library!".format(num_updated))

def test():
    liked_tracks = get_liked_tracks()
    print(len(liked_tracks))
    print(len(get_track_names(liked_tracks)))

    # playlist_names, playlist_name_map, playlist_superlists = get_playlists_info()

    # print_plan(playlist_names, playlist_name_map, playlist_superlists)


if __name__ == "__main__":
    main()

"""
if __name__ == "__main__":
    # user = sp_library_read.user('leothemighty123')
    saved_tracks = sp_library_read.current_user_saved_tracks()

    sublist_map, playlist_name_map = get_sublist_maps()
    # print(sublist_map)

    liked_set = set()

    # 2. Add all playlist items to
    for k, v in playlist_name_map.items():
        print("Adding \"" + k + "\"'s tracks to Liked")


    # 1. Add the regular playlist items to the (personal) playlists
    for k, v in sublist_map.items():
        # update_playlist_from_sub(playlist_name_map[k], playlist_name_map[v])
        # print(k + " is the sublist of " + v)
        print("UPDATING playlist [" + v + "] to have the tracks from sub_playlist [" + k + "]")
        update_playlist_from_sub(playlist_name_map[k], playlist_name_map[v])
"""


