from spotify_helper import SpotifyHelper, LIKED_ID, LIKED_NAME
from log import Log

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

# TODO
RECOMMENDED_ARCHIVE_PLAYLIST_NAME = 'My Archived Recommended Songs'

PREFIX_UPDATE_MAP = {
    "we": ['My Recommended Songs'],
    "": [LIKED_NAME],
    LIKED_ID: ["Cursed combination"],
}

# Init the spotify helper
sp = SpotifyHelper()

# Init the logger
logger = Log(True)

def matches_prefix(name, prefix):
    """Determines whether the name matches the given prefix"""

    return name.replace(IGNORE_CHARACTER, '').lower().startswith(prefix)

def add_to_list_map(d, k, v):
    """Maintains a map of lists by initializing an empty list for a key when it is attempted to put into place.

    Args:
        d (dict): The dictionary to place the value into.
        k (str): The string key where to put the value.
        v (str): The individual value to place into the list for the key.
    """

    if k not in d.keys():
        d[k] = []
    d[k].append(v)

def get_playlists_info():
    """Gets all the necessary playlist info for the user.

    Returns:
        1. playlist_names (dict): The map of playlist IDs to their names.
        2. playlist_name_map (dict): The map of playlist names to the list of IDs that the name is associated with.
        3. playlist_superlists (dict): The map of playlist IDs to the list of super-playlist IDs associated with the playlist that need to get updated.
    """

    # Initialize the map with the name we'll designate for Liked
    playlist_names = { LIKED_ID: LIKED_NAME }
    playlist_name_map = { LIKED_NAME: [LIKED_ID] }
    playlist_superlists = {}

    # Map of to-update playlist name to list of names
    prefix_update_names = {}

    def add_superlist(sub_playlist_name, super_playlist_name):
        """Add a sublist/superlist association.

        Args:
            sub_playlist_name (str): The playlist name for the sub-playlist.
            super_playlist_name (str): The playlist name for the super-playlist.
        """

        for sub_playlist_id in playlist_name_map.get(sub_playlist_name, []):
            for super_playlist_id in playlist_name_map.get( super_playlist_name, []):
                add_to_list_map(playlist_superlists, sub_playlist_id, super_playlist_id)

    def handle_playlist(playlist):
        """The function that will take in every single playlst for the user and populate the return values for the parent function.

        Args:
            playlist (dict): The dictionary returned from the Spotify API containing the information for a playlist.
        """

        playlist_id = playlist['id']
        playlist_name = playlist['name']

        for prefix, names in PREFIX_UPDATE_MAP.items():
            if matches_prefix(playlist_name, prefix):
                prefix_update_names[playlist_name] = names

        playlist_names[playlist_id] = playlist_name
        add_to_list_map(playlist_name_map, playlist_name, playlist_id)

        personal_name = playlist_name + SUPERLIST_INDICATOR
        if personal_name in playlist_name_map:
            add_superlist(playlist_name, personal_name)
        if playlist_name.endswith(SUPERLIST_INDICATOR):
            real_name = playlist_name[:-len(SUPERLIST_INDICATOR)]
            if real_name in playlist_name_map:
                add_superlist(real_name, playlist_name)

    sp.handle_all_playlists(handle_playlist)

    for sub_playlist_name, names in prefix_update_names.items():
        for playlist_name in names:
            add_superlist(sub_playlist_name, playlist_name)

    return playlist_names, playlist_name_map, playlist_superlists

def get_all_playlist_tracks(playlist_names):
    """Gets the map for every single track in every single playlist that the current user owns.

    Args:
        playlist_names ({str: str}): Map of playlist IDs to their corresponding names.

    Returns:
        ({str: set(str)}): The map of playlist IDs to the set of track IDs associated with the track.
    """

    logger.debug("Getting the sets of playlist tracks:")
    logger.debug("")
    playlist_tracks = {}
    for playlist_id, playlist_name in playlist_names.items():
        tracks = get_playlist_tracks(playlist_id)
        logger.debug("\"{}\" has {} tracks".format(playlist_name, len(tracks)))
        playlist_tracks[playlist_id] = tracks

    logger.debug("=" * 20)
    logger.debug("Calculated for {} playlists".format(len(playlist_tracks.keys())))
    logger.debug("=" * 20)
    return playlist_tracks

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
    """Get the tracks to add to each playlist from what's missing.

    Args:
        playlist_superlists ({str: [str]}): The map of playlist IDs to the list of their corresponding super-playlists to potentially update.
        playlist_tracks ({str: set(str)}): The map of playlist ID to the IDs of the tracks within them.
        playlist_names ({str: str}): The map of playlist IDs to their names.

    Returns:
        {str: set(str)}: Map of playlist ID to the set of track ids to add.
    """

    logger.debug("Getting the playlists to update:")
    logger.debug("")
    playlists_to_update = {}
    for sublist, superlists in playlist_superlists.items():
        for superlist in superlists:
            sublist_tracks = playlist_tracks[sublist]
            superlist_tracks = playlist_tracks[superlist]
            missing_tracks = get_missing_tracks(sublist_tracks, superlist_tracks)

            # Ensure that we don't have any empty updates in the map at all
            if len(missing_tracks) != 0:
                print("\"{}\" is missing {} tracks FROM sublist \"{}\"".format(playlist_names[superlist], len(missing_tracks), playlist_names[sublist]))
                if superlist not in playlists_to_update:
                    playlists_to_update[superlist] = set()
                playlists_to_update[superlist].update(missing_tracks)

    logger.debug("=" * 20)
    logger.debug("There are {} playlists to update".format(len(playlists_to_update.keys())))
    logger.debug("=" * 20)

    return playlists_to_update

def update_playlists(playlists_to_update):
    """Update all of the playlist with their missing tracks.

    Args:
        playlists_to_update ({str: set(str)}): The map of playlist IDs to the track IDs to update them with.
    """

    num_updated = 0
    for playlist, track_ids in playlists_to_update.items():
        sp.update_playlist(playlist, list(track_ids))
        num_updated += len(track_ids)
    return num_updated

def print_accomplish_plan():
    """Print the overall plan we want to do. High-level, doesn't look into the current user's details yet, just at the configuration of the script."""

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
    """Print the plan that we want to do to update the library, with specifically which playlists we will update from which other playlists"""

    print("================================")
    print("Playlist update plan:")
    print()
    for sublist, superlists in playlist_superlists.items():
        for superlist in superlists:
            print("{} -> {}".format(playlist_names[sublist], playlist_names[superlist]))
    print()

def print_detailed_track_plan(playlists_to_update, playlist_names):
    """Print the exact plan of which tracks will get added to which playlists"""

    print("================================")
    print("What will get updated:")
    print()
    for playlist, tracks in playlists_to_update.items():
        print("\"{}\" (to add {} tracks):".format(playlist_names[playlist], len(tracks)))
        for i, track_name in enumerate(get_track_names(tracks)):
            print("    {}. {}".format(i, track_name))
        print()

def main():
    """Go through the process of taking user input and telling them exactly what will happen, as well as stopping and letting them check before we actually update anything"""

    print_accomplish_plan()

    playlist_names, playlist_name_map, playlist_superlists = get_playlists_info()

    playlist_tracks = get_all_playlist_tracks(playlist_names)

    playlists_to_update = get_playlists_to_update(playlist_superlists, playlist_tracks, playlist_names)

    print_detailed_track_plan(playlists_to_update, playlist_names)

    print()
    print("Look at the track update plan and make sure it's what you want!!")
    print()
    print("If you're ready to proceed, type \"YES\" to update your library. Anything else will cancel")
    answer = input()
    if answer != "YES":
        print("Aborting...")
        return

    num_updated = update_playlists(playlists_to_update)

    print("Successfully added {} tracks to different playlists in your library!".format(num_updated))

if __name__ == "__main__":
    main()


