# Playlist Manager for Spotify
### By Leo Belyi

## Why?

bro literally my god damn playlists are horrendously hard to manage, whenever I have a song that I like I have to add them to like 5 different playlistsbecause of how I have things organized. I think it might be cool to automate this process a lot faster through a playlist manager.

## What does it do?

I'm thinking of having a chain of updates, so for instance there will be playlists that will automatically update based on other playlists. My "Recommended Songs" should have all the songs that I add to any of my "we listening" playlists.

## Okay now what does it actually do?

Let's start with an "update" function that goes through and makes sure that all of the tracks on my Liked Songs are in both Cursed Combination and My Recommended Songs.

Additionally it should make sure that playlists that have " (personal)" after it and have a corresponding playlist, have all of the songs that the corresponding playlist has. The regular playlist should be a subset.

1. Adds all the regular playlist songs to their corresponding super playlist.
1. Adds every single playlist track to the liked playlist

## Configuration

First of all, to make this work at all you need to run `cp secrets.py.tmp secrets.py` and fill out the information in the file.

TODO: probably not how it should go, i think i need to check in the secrets for anyone to use it. Whatever, I'll figure it out once i get off this bitchin flight, my ears hurt and i don't have wifi :(
