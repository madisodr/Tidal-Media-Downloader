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
import sqlite3

from tidal_dl.paths import *
from tidal_dl.printf import *
from tidal_dl.tidal import *

_connection: sqlite3.Connection = None
database_file = "library.db"

def getConnection() -> sqlite3.Connection:
    global _connection
    if not _connection:
        _connection = sqlite3.connect(database_file)
        print("Successfully connected to SQLite database")

    return _connection

def getCursor() -> sqlite3.Cursor:
    cursor = getConnection().cursor()
    # Assuming you want to use a specific SQLite database schema or file
    cursor.execute(f"ATTACH DATABASE '{database_file}' AS tidal_dl")
    return cursor

def isDatabaseInitialized() -> bool:
    try:
        cursor = getCursor()

        # Check if the tidal_dl database exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='songs'")
        songs_table_exists = cursor.fetchone()

        # Check if the songs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='playlists'")
        playlists_table_exists = cursor.fetchone()

        cursor.close()

        if songs_table_exists and playlists_table_exists:
            print("The tidal_dl database exists, and the songs and playlists tables are present.")
            return True
        elif songs_table_exists or playlists_table_exists:
            print("The tidal_dl database exists, but either the songs table or the playlists table is missing.")
            return False
        else:
            print("The tidal_dl database does not exist.")
            return False
    except sqlite3.Error as error:
        print(f"Error while executing SQL query: {str(error)}")
        return False

def setupDatabase():
    cursor = getCursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS playlists (
        uuid VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        numberOfTracks INT UNSIGNED DEFAULT 0,
        duration INT UNSIGNED DEFAULT 0,
        PRIMARY KEY (uuid)
    )
    """
    try:
        cursor.execute(create_table_sql)
    except sqlite3.Error as error:
        print(f"Error while executing SQL query: {str(error)}")
        return False

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS songs (
        uuid INTEGER PRIMARY KEY AUTOINCREMENT,
        id INT UNSIGNED NOT NULL,
        title VARCHAR(255) NOT NULL,
        artist VARCHAR(255) NOT NULL,
        album VARCHAR(255),
        playlist VARCHAR(255) NOT NULL,
        duration INT UNSIGNED DEFAULT 0,
        trackNumberOnPlaylist INT UNSIGNED DEFAULT 0,
        FOREIGN KEY (playlist) REFERENCES playlists (uuid)
    )
    """
    try:
        cursor.execute(create_table_sql)
    except sqlite3.Error as error:
        print(f"Error while executing SQL query: {str(error)}")
        return False
    
    _connection.commit()

'''
Check to see if a playlists exists in the database already
'''
def checkDatabaseForPlaylist(playlist: Playlist=None) -> bool:
    Printf.info("check db for playlist")
    # skip songs not in a playlist
    if playlist is None:
        return False

    try:
        _cursor = getCursor()

        query = "SELECT COUNT(*) FROM tidal_dl.playlists WHERE uuid = %s"
        values = (playlist.uuid)

        _cursor.execute(query, values)
        result = _cursor.fetchone()

        _cursor.close()

        if result[0] > 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally:
        _cursor.close()

'''
Check to see if a track exists in the database
'''
def checkDatabaseForTrack(track: Track, playlist: Playlist=None) -> bool:
    Printf.info("check db for track")
    # skip songs not in a playlist
    if playlist is None:
        return False

    try:
        _cursor = getCursor()

        # Prepare the SQL query
        query = "SELECT COUNT(*) FROM tidal_dl.songs WHERE id = %s AND playlist = %s"
        values = (track.id, playlist.uuid)

        # Execute the query
        _cursor.execute(query, values)
        result = _cursor.fetchone()

        _cursor.close()

        if result[0] > 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally:
        _cursor.close()


def addTrackToDatabase(track: Track, playlist: Playlist=None):
    Printf.info("add track to db")

    if playlist is None:
        return True

    try:
        _cursor = getCursor()

        # Insert the playlist if it doesn't exist
        insert_playlist_query = "INSERT INTO tidal_dl.playlists (uuid, title, numberOfTracks, duration) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title), numberOfTracks=VALUES(numberOfTracks), duration=VALUES(duration)"
        playlist_values = (playlist.uuid, playlist.title, playlist.numberOfTracks, playlist.duration)
        _cursor.execute(insert_playlist_query, playlist_values)

        # Insert the track into the songs table
        insert_track_query = "INSERT INTO tidal_dl.songs (id, title, artist, album, playlist, duration, trackNumberOnPlaylist) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        track_values = (track.id, track.title, track.artist.name, track.album.title, playlist.uuid, track.duration, track.trackNumberOnPlaylist)
        _cursor.execute(insert_track_query, track_values)

        # Commit the changes to the database
        _connection.commit()

        return True
    except sqlite3.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally:
        _cursor.close()
