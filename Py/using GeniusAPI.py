
##CREATE A VARIABLE INPUT for the DNN save the W and b and feed again // change Batch size

import requests
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import db_get_requests as db_get
import genius_API_requests as GAPI
import db_insert_requests as db_ins




def main():
    artist_list = {}
    artist_without_songs = db_get.get_artists_without_songs_in_db()
    artists_with_songs = db_get.get_artists_with_songs_in_db()
    artists_ids = db_get.get_list_artists()
    existing_songs = db_get.get_existing_songs()

            #Grabs all song id's from one artist
    songs_ids=GAPI.get_song_id(56)
    
            # Get meta information about songs
    #song_list = get_song_information(songs_ids)
    
            # Add songs of the artist to the DB
    #add_songs(song_list)
    
            #Grab all featuring artists from songs ID
    #artist_list = get_other_artists_from_songs(songs_ids)
    
            #add new artists to the DB
    #add_artists(artist_list)
    
            #Grabs from Genius all song id's from artists''' 
    #get_songs_of_all_artists(artists_ids, artist_without_songs, existing_songs)
    
if __name__ == "__main__":
    main()
