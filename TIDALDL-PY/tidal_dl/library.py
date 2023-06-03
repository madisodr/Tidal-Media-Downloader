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
import mysql.connector
import mysql.connector.cursor

from tidal_dl.paths import *
from tidal_dl.printf import *
from tidal_dl.tidal import *


_connection:mysql.connector.MySQLConnection = None

def getConnection() -> mysql.connector.MySQLConnection:
    global _connection
    if not _connection:
        # TODO make these params configurable via settings
        _connection =  mysql.connector.connect(host="localhost", user="root", password="passwd") 

        Printf.info("sucessfully connected to mysql database")

    return _connection

def getCursor() -> mysql.connector.cursor.MySQLCursor:
    cursor = getConnection().cursor()
    cursor.execute("USE tidal_dl")    
    return cursor

def isDatabaseInitialized() -> bool:
    try:
        _cursor = getCursor()

        _cursor.execute("SHOW DATABASES LIKE 'tidal_dl'")
        database_exists = _cursor.fetchone()

        if database_exists:
            _cursor.execute("USE tidal_dl")
            # Check if the songs table exists
            _cursor.execute("SHOW TABLES LIKE 'songs'")
            songs_table_exists = _cursor.fetchone()

            # Check if the playlists table exists
            _cursor.execute("SHOW TABLES LIKE 'playlists'")
            playlists_table_exists = _cursor.fetchone()

            _cursor.close()
            if songs_table_exists and playlists_table_exists:
                Printf.info("The tidal_dl database exists, and the songs and playlists tables are present.")
                return True
            else:
                Printf.info("The tidal_dl database exists, but either the songs table or the playlists table is missing.")
                return False

        else:
            Printf.info("The tidal_dl database does not exist.")
            return False
    except mysql.connector.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally: 
        _cursor.close()
    

def setupDatabase():
    try:
        _cursor = getCursor()
        with open ('sql/setup.sql', 'r') as file:
            sql_statements = file.read()
        
        _cursor.execute(sql_statements)
    except mysql.connector.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally: 
        _cursor.close()

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
    except mysql.connector.Error as error:
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
    except mysql.connector.Error as error:
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
    except mysql.connector.Error as error:
        Printf.err(f"Error while executing SQL query: {str(error)}")
        return False
    finally: 
        _cursor.close()
