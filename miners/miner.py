import MySQLdb as mdb
import pylast
from musixmatch import Musixmatch
from yandex_translate import YandexTranslate

LFM_API_KEY = ""
LFM_API_SECRET = ""
MM_API_KEY = ""
YANDEX_KEY = ""

# In order to perform a write operation you need to authenticate yourself
username = ""
password_hash = pylast.md5("")


def get_title_and_artist_from_item(item):
    split = item.split(" - ")
    return split[0], split[1]


# insert new artist to artists table with data from last FM
# checks that artist doesn't exist already using artist_id
def insert_new_artist_lfm(con, artist_name, artist_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT artist_id FROM artists WHERE name = %s", artist_name)
        if cur.rowcount == 0:
            cur.execute("INSERT INTO artists (artist_id, name) VALUES(%s, %s)", (artist_counter, artist_name))
            return artist_counter
        else:
            return cur.fetchone()[0]


# insert new album to albums table with data from last FM
# checks that album doesn't exist already using album name and artist_id
def insert_new_album_lfm(con, album_name, artist_id, album_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT album_id FROM albums WHERE name = %s AND artist_id = %s", (album_name, artist_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO albums (album_id, name, artist_id) VALUES(%s, %s, %s)",
                        (album_counter, album_name, artist_id))
            return album_counter
        else:
            return cur.fetchone()[0]


# insert new song to songs table with data from last FM
# checks that song doesn't exist already using song name and artist_id
def insert_new_song_lfm(con, title, artist_id, album_id, song_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT song_id FROM songs WHERE name = %s AND artist_id = %s",
                    (title, artist_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO songs (song_id, name, album_id, artist_id) VALUES(%s, %s, %s, %s)",
                        (song_counter, title, album_id, artist_id))
            return song_counter
        else:
            return cur.fetchone()[0]

# gets tracks from last FM, then inserts new artist and song to tables if they don't exist
def get_tracks_last_fm():
    network = pylast.LastFMNetwork(api_key=LFM_API_KEY, api_secret=LFM_API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('', '', '', "")
    chart_songs = network.get_top_tracks(1000)
    artist_counter = 0
    album_counter = 0
    song_counter = 0
    for song in chart_songs:
        artist, title = get_title_and_artist_from_item(str(song.item))
        artist_id = insert_new_artist_lfm(con, artist, artist_counter)
        insert_new_song_lfm(con, title, artist_id, -1, song_counter)
        artist_counter += 1
        album_counter += 1
        song_counter += 1

# insert new artist to artists table with data from musixmatch
# checks that artist doesn't exist already using artist_id
def insert_new_artist_mm(con, artist_name, artist_id):
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM artists WHERE artist_id = %s", artist_id)
            if cur.rowcount == 0:
                cur.execute("INSERT INTO artists (artist_id, name) VALUES(%s, %s)", (artist_id, artist_name))
    except:
        pass


def insert_new_album_mm(con, album_id, name, artist_id, cover, rating=-1):
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT album_id FROM albums WHERE album_id = %s", album_id)
            if cur.rowcount == 0:
                cur.execute("INSERT INTO albums (album_id, name, artist_id, cover, rating) VALUES(%s, %s, %s, %s, %s)",
                            (album_id, name, artist_id, cover, rating))
    except:
        pass


def insert_new_song_mm(con, song_id, title, lyrics_id, album_id, artist_id, rating):
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT song_id FROM songs WHERE song_id = %s", song_id)
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO songs (song_id, title, lyrics_id, album_id, artist_id, rating) VALUES(%s, %s, %s, %s, %s, %s)",
                    (song_id, title, lyrics_id, album_id, artist_id, rating))
    except:
        pass


def get_artist_ratings():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        cur.execute("SELECT artist_id FROM artists WHERE rating IS NULL")
        everything_list = []
        for i in range(cur.rowcount):
            id = cur.fetchone()[0]
            artist = musixmatch.artist_get(id)
            country = artist.get('message').get('body').get('artist').get('artist_country')
            rating = artist.get('message').get('body').get('artist').get('artist_rating')
            everything_list.append((country, rating, id))
        for item in everything_list:
            cur.execute("UPDATE artists SET country = %s, rating = %s WHERE artist_id = %s", item)


def get_album_ratings():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        cur.execute("SELECT album_id FROM albums WHERE rating IS NULL")
        everything_list = []
        for i in range(cur.rowcount):
            id = cur.fetchone()[0]
            album = musixmatch.album_get(id)
            # release_date = album.get('message').get('body').get('album').get('album_release_date')
            rating = album.get('message').get('body').get('album').get('album_rating')

            everything_list.append((rating, id))
        for item in everything_list:
            cur.execute("UPDATE albums SET rating = %s WHERE album_id = %s", item)


def get_tracks_musixmatch():
    try:
        musixmatch = Musixmatch(MM_API_KEY)
        con = mdb.connect('localhost', 'root', 'Armageddon1', 'musixmatch')
        for i in range(1, 10):
            chart = musixmatch.chart_tracks_get(i, 100, 0, country='il')
            list_of_tracks = chart.get('message').get('body').get('track_list')
            for j in range(100):
                track = list_of_tracks[j].get('track')
                song_id = track.get('track_id')
                title = track.get('track_name')
                lyrics_id = track.get('lyrics_id')
                album_id = track.get('album_id')
                album_name = track.get('album_name')
                artist_id = track.get('artist_id')
                artist_name = track.get('artist_name')
                album_cover = track.get('album_coverart_100x100')
                rating = track.get('track_rating')
                insert_new_artist_mm(con, artist_name, artist_id)
                insert_new_album_mm(con, album_id, album_name, artist_id, album_cover)
                insert_new_song_mm(con, song_id, title, lyrics_id, album_id, artist_id, rating)

            # print chart
    except:
        pass


def get_all_albums_from_artists():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        cur.execute("SELECT artist_id FROM artists")
        list_of_lists_of_albums = list()
        for i in range(cur.rowcount):
            id = cur.fetchone()[0]
            for j in range(1, 5):
                list_of_lists_of_albums.append(
                    musixmatch.artist_albums_get(id, 1, j, 100, 'desc').get('message').get('body').get('album_list'))
        for lst in list_of_lists_of_albums:
            for album in lst:
                album = album.get('album')
                artist_id = album.get('artist_id')
                album_id = album.get('album_id')
                album_name = album.get('album_name')
                rating = album.get('album_rating')
                album_cover = album.get('album_coverart_100x100')
                insert_new_album_mm(con, album_id, album_name, artist_id, album_cover, rating)


def insert_new_tracks_from_list(con, list_of_lists_of_songs):
    for lst in list_of_lists_of_songs:
        for song in lst:
            song = song.get('track')
            song_id = song.get('track_id')
            lyrics_id = song.get('lyrics_id')
            title = song.get('track_name')
            rating = song.get('track_rating')
            artist_id = song.get('artist_id')
            album_id = song.get('album_id')
            # album_cover = song.get('album_coverart_100x100')
            insert_new_song_mm(con, song_id, title, lyrics_id, album_id, artist_id, rating)


def get_all_tracks_from_albums():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        list_of_lists_of_songs = list()
        try:
            cur.execute(
                "SELECT album_id, album_mbid FROM albums WHERE album_mbid IS NOT NULL")
            for i in range(cur.rowcount):
                row = cur.fetchone()
                album_id, album_mbid = row[0], row[1]
                ll = musixmatch.album_tracks_get(album_id, 1, 100, album_mbid).get('message')
                list_of_lists_of_songs.append(ll.get('body').get('track_list'))
            insert_new_tracks_from_list(con, list_of_lists_of_songs)
        except Exception as e:
            print "error occurred: "
            print e.message
            print "size of list of lists: " + str(len(list_of_lists_of_songs))
            insert_new_tracks_from_list(con, list_of_lists_of_songs)


def update_albums_release_date_and_type(cur, dict_of_dates):
    for album_id in dict_of_dates:
        month = dict_of_dates[album_id][0]
        year = dict_of_dates[album_id][1]
        album_type = dict_of_dates[album_id][2]
        if year != '':
            if month != '':
                cur.execute(
                    "UPDATE albums SET type = %s, release_year = %s, release_month = %s WHERE album_id = %s",
                    (album_type, year, month, album_id))
            else:
                cur.execute(
                    "UPDATE albums SET type = %s, release_year = %s WHERE album_id = %s",
                    (album_type, year, album_id))


def update_album_mbid(cur, dict_of_mbids):
    for album_id in dict_of_mbids:
        album_mbid = dict_of_mbids[album_id]
        cur.execute(
            "UPDATE albums SET album_mbid = %s WHERE album_id = %s",
            (album_mbid, album_id))


def get_mbid_from_albums():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        dict_of_mbids = dict()
        try:
            cur.execute("SELECT album_id FROM albums WHERE albums.album_mbid IS NULL")
            for i in range(cur.rowcount):
                album_id = cur.fetchone()[0]
                album = musixmatch.album_get(album_id).get('message').get('body').get('album')
                album_mbid = album.get('album_mbid')
                dict_of_mbids.update({album_id: album_mbid})
        except Exception as e:
            print "error occurred: "
            print e.message
            print "size of dict: " + str(len(dict_of_mbids))
        update_album_mbid(cur, dict_of_mbids)


def get_release_dates_albums_and_types():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        dict_of_dates = dict()
        try:
            cur.execute("SELECT album_id FROM albums WHERE type IS NULL")
            for i in range(cur.rowcount):
                album_id = cur.fetchone()[0]
                album = musixmatch.album_get(album_id).get('message').get('body').get('album')
                release_date = album.get('album_release_date')
                album_type = album.get('album_release_type')
                release_date = release_date.split('-')
                year = -1
                month = -1
                if len(release_date) > 0:
                    year = release_date[0]
                    if len(release_date) > 1:
                        month = release_date[1]
                dict_of_dates.update({album_id: (month, year, album_type)})
            update_albums_release_date_and_type(cur, dict_of_dates)
        except Exception as e:
            print "error occurred: "
            print e.message
            print "size of dict: " + str(len(dict_of_dates))
            update_albums_release_date_and_type(cur, dict_of_dates)


def insert_into_lyrics(cur, dict_of_lyrics):
    for song_id in dict_of_lyrics:
        try:
            cur.execute("SELECT song_id FROM lyrics WHERE song_id = %s", song_id)
            if cur.rowcount == 0:
                text = dict_of_lyrics[song_id][0]
                src_language = dict_of_lyrics[song_id][1]
                cur.execute(
                    "INSERT INTO lyrics (song_id, text, src_lang) VALUES(%s, %s, %s)", (song_id, text, src_language))
        except Exception as e:
            print "error occurred: "
            print e.message


def get_existing_lyrics(con):
    cur = con.cursor()
    set_of_ids = set()
    cur.execute("SELECT song_id FROM lyrics")
    for i in range(cur.rowcount):
        set_of_ids.add(cur.fetchone()[0])
    return set_of_ids


def get_lyrics_of_tracks():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    con.set_character_set('utf8')
    with con:
        cur = con.cursor()
        cur.execute('SET CHARACTER SET utf8')
        cur.execute('SET character_set_connection=utf8')
        dict_of_lyrics = dict()
        set_of_existing_ids = get_existing_lyrics(con)
        try:
            cur.execute("SELECT song_id FROM songs")
            for i in range(cur.rowcount):
                song_id = cur.fetchone()[0]
                if song_id not in set_of_existing_ids:
                    message = musixmatch.track_lyrics_get(song_id).get('message')
                    if message.get('header').get('status_code') == 200:
                        lyrics = message.get('body').get('lyrics')
                        text = lyrics.get('lyrics_body')
                        src_language = lyrics.get('lyrics_language')
                        dict_of_lyrics.update({song_id: (text, src_language)})
        except Exception as e:
            print "error occurred: "
            print e.message
            print "size of dict: " + str(len(dict_of_lyrics))
        insert_into_lyrics(cur, dict_of_lyrics)


def insert_into_lyrics_translation(cur, dict_of_lyrics):
    for song_id in dict_of_lyrics:
        try:
            translation = dict_of_lyrics[song_id][0]
            cur.execute(
                "UPDATE lyrics SET translation = %s WHERE song_id =  %s", (translation, song_id))
        except Exception as e:
            print "error occurred: "
            print e.message
            print e.args
    # get_lyrics_translation()


def get_lyrics_translation():
    translate = YandexTranslate('trnsl.1.1.20171218T200252Z.d74bdb39ed5665a9.5314bb5a519d4d4d70774e148276d6bf69d2d4ae')
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    con.set_character_set('utf8')
    with con:
        cur = con.cursor()
        cur.execute('SET CHARACTER SET utf8')
        cur.execute('SET character_set_connection=utf8')
        dict_of_lyrics = dict()
        try:
            cur.execute("SELECT song_id, text, src_lang FROM lyrics WHERE text != '' AND translation IS NULL")
            if cur.rowcount == 0:
                exit(0)
            for i in range(cur.rowcount):
                row = cur.fetchone()
                song_id = row[0]
                text = row[1]
                src_language = row[2]
                if src_language == '':
                    src_language = 'en'
                message = translate.translate(text, src_language + '-he')
                if message.get('code') == 200:
                    translation = message.get('text')
                    dict_of_lyrics.update({song_id: translation})
                else:
                    print message.get('code')
        except Exception as e:
            print "error occurred: "
            print e.message
            print "size of dict: " + str(len(dict_of_lyrics))
        insert_into_lyrics_translation(cur, dict_of_lyrics)


def insert_popular_songs_to_table(country, list_of_songs):
    print 'starting insert: size = ' + str(len(list_of_songs))
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    con.set_character_set('utf8')

    with con:
        cur = con.cursor()
        cur.execute('SET CHARACTER SET utf8')
        cur.execute('SET character_set_connection=utf8')
        for song in list_of_songs:
            song_name = song[0].encode('utf-8')
            artist_name = song[1].encode('utf-8')
            playcount = song[2]
            album_cover = song[3].encode('utf-8')
            try:
                cur.execute(
                    "INSERT INTO popular_songs (country_name, song_name, artist_name, playcount, album_cover) VALUES(%s, %s, %s, %s,%s)",
                    (country, song_name, artist_name, playcount, album_cover))
                print 'inserted song: ' + song_name
                # cur.execute(
                #     "SELECT * FROM popular_songs_by_country WHERE country_name = %s AND song_name = %s AND artist_name = %s",
                #     (country, song_name, artist_name))
                # if cur.rowcount == 0:

                # else:
                #     print 'song exists'
            except Exception as e:
                print "error occurred: couldn't insert song name: " + song_name
                print e.message


def insert_popular_song_to_table(con, country, title, artist_name, playcount, album_cover, rank):
    with con:
        cur = con.cursor()
        cur.execute('SET CHARACTER SET utf8')
        cur.execute('SET character_set_connection=utf8')
        cur.execute(
            "SELECT * FROM musixmatch.popular_songs WHERE country_name = %s AND title = %s AND artist_name = %s",
            (country, title, artist_name))
        if cur.rowcount == 0:
            try:
                cur.execute(
                    "INSERT INTO musixmatch.popular_songs (country_name, title, artist_name, playcount, album_cover, rank) VALUES(%s, %s, %s, %s,%s)",
                    (country, title, artist_name, playcount, album_cover, rank))
            except Exception as e:
                print "error occurred: couldn't insert song name: " + title
                print e.message
        else:
            update_popular(con, title, artist_name, rank, country)


def get_top_tracks_by_country(country, limit):
    network = pylast.LastFMNetwork(api_key=LFM_API_KEY, api_secret=LFM_API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    con.set_character_set('utf8')
    # list_of_tracks = list()
    geo_songs = network.get_geo_top_tracks(country=country, limit=limit)
    for i in range(len(geo_songs)):
        track = geo_songs.pop()
        try:
            track_item = track.item
            title = track_item.title.encode('utf-8')
            artist = track_item.artist.get_name().encode('utf-8')
            playcount = track_item.get_playcount()
            album = track_item.get_album()
            album_cover = album.get_cover_image().encode('utf-8')
            insert_popular_song_to_table(con, country, title, artist, playcount, album_cover)
            # list_of_tracks.append((title, artist, playcount, album_cover))
        except Exception as e:
            print "error occurred: "
            print e.message
            # print "size of list: " + str(len(list_of_tracks))
    # insert_popular_songs_to_table(country, list_of_tracks)


def update_popular(con, title, artist_name, rank, country_name):
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE musixmatch.popular_songs SET rank = %s WHERE country_name = %s AND title = %s AND artist_name = %s", (rank, country_name, title, artist_name))


def get_rank_of_popular_songs(country_name, limit):
    network = pylast.LastFMNetwork(api_key=LFM_API_KEY, api_secret=LFM_API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    con.set_character_set('utf8')
    # list_of_tracks = list()
    geo_songs = network.get_geo_top_tracks(country=country_name, limit=limit)
    rank = 0
    for i in range(len(geo_songs)):
        track = geo_songs.pop(0)
        try:
            track_item = track.item
            title = track_item.title.encode('utf-8')
            artist = track_item.artist.get_name().encode('utf-8')
            playcount = track_item.get_playcount()
            album = track_item.get_album()
            album_cover = album.get_cover_image().encode('utf-8')
            rank += 1
            insert_popular_song_to_table(con, country_name, title, artist, playcount, album_cover, rank)
            # list_of_tracks.append((title, artist, playcount, album_cover))
        except Exception as e:
            print "error occurred: "
            print e.message


if __name__ == '__main__':
    # get_tracks_musixmatch()
    # get_artist_ratings()
    # get_album_ratings()
    # get_all_albums_from_artists()
    # get_release_dates_albums_and_types()
    # get_mbid_from_albums()
    # get_all_tracks_from_albums()
    # get_lyrics_of_tracks()
    # get_lyrics_translation()
    # get_top_tracks_by_country("United States", 200)
    # lst = {'Argentina', 'France', 'Israel', 'Spain', 'United Kingdom', 'United States'}
    lst = {'Argentina', 'Spain'}
    for country in lst:
        get_rank_of_popular_songs(country, 200)
