from pymongo import MongoClient
import re

'''DB Insert requests'''
#add new artists to our DB
def add_artists(artists):
    for artist in artists:
        entry = {
            'id' : int(artists[artist]['id']),
            'name' : artists[artist]['name'],
            'url' : artists[artist]['url'],
        }
        #Step 3: Insert business object directly into MongoDB via isnert_one
        result=db.artists.insert_one(entry)
        print('artists {} added with success'.format(artists[artist]['name']))

def add_songs(songs):
    '''add new songs to the DB'''
    existing_songs = get_existing_songs()
    entry={}
    for i in songs:
        if not songs[i]['id'] in existing_songs: 
            entry = {
                "id" : songs[i]['id'],
                "url": songs[i]["url"],
                "title": songs[i]["title"],
                "primary_artists" : songs[i]["primary_artists"],
                "album": songs[i]["album"],
                "release_date": songs[i]["release_date"],
                "featured_artists":
                    {feat : songs[i]["featured_artists_id"][j] 
                     if songs[i]["featured_artists"] else "" for j, feat in enumerate(songs[i]["featured_artists"])},
                #"featured_artists_id":
                #    [feat if songs[i]["featured_artists"] else "" for feat in songs[i]["featured_artists_id"]],
                "genius_track_id": songs[i]["genius_track_id"],
                "genius_album_id": songs[i]["genius_album_id"]
            }
            #Step 3: Insert business object directly into MongoDB via isnert_one
            result=db.songs.insert_one(entry)
            #Step 4: Print to the console the ObjectID of the new document
            print('added to DB as {0}'.format(songs[i]['title']))
    #Step 5: Tell us that you are done
    print('finished adding songs')

def add_lyrics():
    '''add lyrics of the songs in DB'''
    songs = get_existing_songs()
    song_ids=[]
    songs_not_to_scrap = get_songs_with_lyrics_scrapped()
    for i,song in enumerate(songs):
        if not song[0] in songs_not_to_scrap:
            parts_indexes = []
            parts_labels = []
            dic_lyrics = {}
            song_parts =[]

            #Get the lyrics of the song
            full_lyrics = retrieve_lyrics(song[0])

            #we can manipulate the lyrics and devide them into 
            splitted_lyrics=re.split("\n+", full_lyrics)
            for j,lyric in enumerate(splitted_lyrics):
                if re.search('\[(.*)\]',lyric):
                    parts_indexes.append(j)
                    lyric = re.search('\[(.*)\]',lyric)
                    parts_labels.append(lyric.group(1))
                    part_of_the_song = ''
                    for k,search_for_next_part in enumerate(splitted_lyrics[j+1:]):
                        next_part_found = False
                        if not next_part_found:
                            if re.search('\[(.*)\]',search_for_next_part) or k>len(splitted_lyrics)-5:
                                next_part_found = True
                                j=k-1
                                break
                            else:
                                '''concatinating lyrics'''
                                part_of_the_song = part_of_the_song+'\n'+search_for_next_part
                    song_parts.append(part_of_the_song)
        
        dic_lyrics['song_id'] = int(song[0])
        for i, indexes in enumerate(parts_indexes):
            dic_lyrics[re.sub(r"[^\w\s]", ' ',parts_labels[i])] = song_parts[i]
            if is_tagged_verse(r"[^\w\s]", ' ',parts_labels[i]):
                result = db.verses.insert_one({'song_id':int(song[0]),'verse':song_parts[i]})
        if parts_indexes:
            result=db.lyrics.insert_one(dic_lyrics)
            print(dic_lyrics)
        

def add_verses():
    '''Add the verses to The DB with the song ID'''
    lyrics = get_all_lyrics()
    for lyric in lyrics:
        print(lyric['song_id'])
        verses=[]
        verses=get_verses_from_lyrics(lyric)
        for verse in verses:
            db.verses.insert_one({'song_id' : lyric['song_id'],'verse' : verse})
