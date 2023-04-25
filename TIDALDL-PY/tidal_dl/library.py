#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   library.py
@Time    :   2023/18/4
@Author  :   madisodr
@Version :   1.0
@Contact :   drmadman92@gmail.com
@Desc    :   keep track of already downloaded files, even if the files name has changed
'''
import csv
import os

from tidal_dl.paths import *
from tidal_dl.printf import *
from tidal_dl.tidal import *
'''
Check to see if a track exists in the database
trackname, artist
'''

def checkDatabaseForTrack(track: Track, playlist=None):
    if playlist is not None and SETTINGS.usePlaylistFolder:
        ppath = getPlaylistPath(playlist)
        if not os.path.exists(ppath):
            Printf.info("path doesn't exist" + ppath)
            os.makedirs(ppath)


    path = getDatabasePath(track, playlist)
    mode = 'r' if os.path.exists(path) else 'w'
    try:
        with open(path, mode) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if track.title == row[0] and track.artist.name == row[1]:
                    return True
    except FileNotFoundError:
        return False

    return False

def addTrackToDatabase(track: Track, album=None, playlist=None):
    path = getDatabasePath(track, playlist)

    Printf.info(f"Adding track {track.title} - {track.artist.name} to {path}")
    with open(path, 'a+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([track.title, track.artist.name])
