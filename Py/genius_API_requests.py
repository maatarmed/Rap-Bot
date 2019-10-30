import requests
import urllib.request
import urllib.parse
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import db_insert_requests
import db_get_requests

#Genius API Requests#

#genius API base and client_token
base = "https://api.genius.com"
client_access_token = "z1va0QLLfH2tm_2NErEGiCUvLUJS0RMBMzfx17EEzUnj3wvJOu4_Dvjx6CNJyJSW"

#to get the response in json format ***
def get_json(path, params=None, headers=None):
	# Generate request URL
	requrl = '/'.join([base, path])
	token = "Bearer {}".format(client_access_token)
	if headers:
		headers['Authorization'] = token
	else:
		headers = {"Authorization": token}

	# Get response object from querying genius api
	response = requests.get(url=requrl, params=params, headers=headers)
	response.raise_for_status()
	return response.json()

def search(artist_name):
	#Search Genius API via artist name.#
	search = "/search?q="
	query = base + search + urllib.parse.quote(artist_name)
	print(query)
	request = urllib.request.Request(query)

	request.add_header("Authorization", "Bearer " + client_access_token)
	request.add_header("User-Agent", "")
	
	response = urllib.request.urlopen(request, timeout=3)
	raw = response.read()
	data = json.loads(raw)['response']['hits']

	for item in data:
		# Print the artist and title of each result
		print(item['result']['primary_artist']['name']
			  + ': ' + item['result']['title'])

def search_artist(artist_id):
	#Search meta data about artist Genius API via Artist ID.#
	search = "artists/"
	path = search + str(artist_id)
	request = get_json(path)
	data = request['response']['artist']

	print(data["followers_count"])
	# Lots of information we can scrape regarding the artist, check keys
	return data["followers_count"] # number of followers

def connect_lyrics(song_id):
	#Constructs the path of song lyrics.#
	url = "songs/{}".format(song_id)
	data = get_json(url)

	# Gets the path of song lyrics
	path = data['response']['song']['path']

	return path

def retrieve_lyrics(song_id):
	#Retrieves lyrics from html page.#
	path = connect_lyrics(song_id)

	URL = "http://genius.com" + path
	page = requests.get(URL)

	# Extract the page's HTML as a string
	html = BeautifulSoup(page.text, "html.parser")

	# Scrape the song lyrics from the HTML
	lyrics = html.find("div", class_="lyrics").get_text()
	return lyrics



def get_song_id(artist_id):
	#Get all the song id from an artist.#
	current_page = 1
	next_page = True
	songs = [] # to store final song ids

	while next_page:
		path = "artists/{}/songs/".format(artist_id)
		params = {'page': current_page} # the current page
		data = get_json(path=path, params=params) # get json of songs
		page_songs = data['response']['songs']
		if page_songs:
			# Add all the songs of current page
			songs += page_songs
			# Increment current_page value for next loop
			current_page += 1
			print("Page {} finished scraping".format(current_page))
			# If you don't wanna wait too long to scrape, un-comment this
			#if current_page == 2:
			 #   break
		else:
			# If page_songs is empty, quit
			next_page = False

	print("Song id were scraped from {} pages".format(current_page))

	# Get all the song ids, excluding not-primary-artist songs.
	songs = [song["id"] for song in songs
	if song["primary_artist"]["id"] == artist_id]

	return songs

#get the informations of a song
def get_song_information(song_ids):
	song_list = {}
	print("Scraping song information")
	for i, song_id in enumerate(song_ids):
		print("id:" + str(song_id) + " start. ->")

		path = "songs/{}".format(song_id)
		data = get_json(path=path)["response"]["song"]

		song_list.update({
		i: {
			"id" : data['id'],
			"url": data["url"],
			"title": data["title"],
			"primary_artists" : {re.sub(r"[^\w\s]", ' ', data["primary_artist"]['name']):data["primary_artist"]['id']},
			"album": data["album"]["name"] if data["album"] else "<single>",
			"release_date": data["release_date"] if data["release_date"] else "unidentified",
			"featured_artists":
			[re.sub(r"[^\w\s]", ' ', feat["name"]) if data["featured_artists"] else "" for feat in data["featured_artists"]],
			"featured_artists_id":
			[feat['id'] if data["featured_artists"] else "" for feat in data["featured_artists"]],
			"genius_track_id": song_id,
			"genius_album_id": data["album"]["id"] if data["album"] else "none"}
		})

		print("-> id:" + str(data['title']) + " is finished. \n")
	return song_list

#def get_producers():


def get_other_artists_from_songs(song_ids):
	#Retrieve meta data about a song.#
	# initialize existing artists and a dictionary for new artists.
	existing_artists = get_list_artists()
	artist_list ={}
	print("Scraping song information")
	for i, song_id in enumerate(song_ids):
		print("id:" + str(song_id) + " start. ->")
		path = "songs/{}".format(song_id)
		data = get_json(path=path)["response"]["song"]
		if data["featured_artists"]:
			for artist in data["featured_artists"]:
				if not artist['id'] in existing_artists:
					artist_list.update({
					int(artist["id"]): {
					"id": int(artist["id"]),
					"url": artist["url"],
					"name": artist["name"]}
					})
		if data["primary_artist"]:
			if not data["primary_artist"]["id"] in existing_artists:
				artist_list.update({
				int(data["primary_artist"]["id"]): {
				"id": int(data["primary_artist"]["id"]),
				"url": data["primary_artist"]["url"],
				"name": data["primary_artist"]["name"]}
				})

		print("-> id:" + str(song_id) + " is finished. \n")

	return artist_list  

def get_songs_of_all_artists(artists_ids, artist_without_songs, existing_songs):
	#Grabs all song id's from artists# 
	for artist_id in artists_ids:
		if artist_id in artist_without_songs:
			songs_ids=[]
			song_list = []
			songs_ids_of_an_artist = get_song_id(artist_id)
			for song in songs_ids_of_an_artist:
	#To not scrap songs we already have#
				if not song in existing_songs:
					songs_ids.append(song)
					song_list = get_song_information(songs_ids)
					add_songs(song_list)
					print('songs added to DB')
	print('done')
