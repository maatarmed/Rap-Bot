
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

#DB connexion
global client
client = MongoClient(port=27017)
global db
db=client.GeniusScrappingProject

#DB Get requests#
def get_existing_songs():
	#Returns a list of the songs and their primary artists#
	songs = db.songs.find()
	existing_songs = []
	for song in songs:
		existing_songs.append([song['id'], song['primary_artists'].items()])
	return existing_songs

def get_songs_with_lyrics_scrapped():
	#Returns the list of songs ids that lyrics has been already added to DB#
	songs_scrapped =[]
	lyrics = db.lyrics.find()
	for song_id in lyrics:
		songs_scrapped.append(song_id['song_id'])
	return songs_scrapped

def get_primary_artists_from_songs():
	#Returns the primary artist of all the songs in the DB#
	songs = db.songs.find()
	existing_songs = {}
	for i, song in enumerate(songs):
		existing_songs.update({
		song['primmary_artists']
		})
	return existing_songs

#returns list of IDs of the artists we have in the DB
def get_list_artists():
#Returns all artists from DB#
	artists = db.artists.find()
	existing_artists = []
	for artist in artists:
		existing_artists.append(artist['id'])
	return existing_artists

def get_artists_without_songs_in_db():
	#Returns artists that don't have songs in ou DB#
	all_artists = get_list_artists()
	artists_with_songs = get_artists_with_songs_in_db()
	artists_without_songs = []
	for artist in all_artists:
		if not artist in artists_with_songs:
			artists_without_songs.append(artist)
	return artists_without_songs

def get_artists_with_songs_in_db():
	#Returns artists that have songs in ou DB#
	existing_songs = get_existing_songs()
	artists_with_songs=[]
	list_atists = get_list_artists()
	for song in existing_songs:
		if sorted(song[1])[0][1] in list_atists:
			artists_with_songs.append(sorted(song[1])[0][1])
	artists_with_songs = list(set(artists_with_songs))
	return artists_with_songs

def get_verses_from_lyrics(lyrics):
	#Returns a list of verses from lyrics#
	verses = []
	lyrics_keys = list(lyrics.keys())
	for key in lyrics_keys:
		if is_tagged_verse(key):
			verses.append(lyrics[key])
	return verses

def get_all_lyrics():
	#Returns the lyrics from DB#
	existing_lyrics = db.lyrics.find()
	all_lyrics = []
	for lyrics in existing_lyrics:
		all_lyrics.append(lyrics)
	return all_lyrics
