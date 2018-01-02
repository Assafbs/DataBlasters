import MySQLdb as mdb
import pylast
import spotipy
from musixmatch import Musixmatch
from yandex_translate import YandexTranslate

LFM_API_KEY = "d202d3c8b0726f003b32954d7d37e6ab"
LFM_API_SECRET = "186006795c45cabe0d4692cd8dd6b01c"
MM_API_KEY = "3dbef1b0188814ddcc0f7bdd95ed9902"
YANDEX_KEY = 'trnsl.1.1.20171218T200252Z.d74bdb39ed5665a9.5314bb5a519d4d4d70774e148276d6bf69d2d4ae'
SPOTIPY_CLIENT_ID = '8d8c1e0464d4491b93a0147b562a9977'
SPOTIPY_CLIENT_SECRET = 'c30c18cb45584824b8ff7622d54a02ff'
SPOTIPY_USERNAME = '0owuj9cx9fcccdyherjzgb8rf'

# In order to perform a write operation you need to authenticate yourself
username = "lederdavid"
password_hash = pylast.md5("Armageddon1!")


def get_title_and_artist_from_item(item):
    split = item.split(" - ")
    return split[0], split[1]


def insert_new_artist_lfm(con, artist_name, artist_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT artist_id FROM artists WHERE name = %s", artist_name)
        if cur.rowcount == 0:
            cur.execute("INSERT INTO artists (artist_id, name) VALUES(%s, %s)", (artist_counter, artist_name))
            # artist_counter += 1
            return artist_counter
        else:
            return cur.fetchone()[0]


def insert_new_album_lfm(con, album_name, artist_id, album_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT album_id FROM albums WHERE name = %s AND artist_id = %s", (album_name, artist_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO albums (album_id, name, artist_id) VALUES(%s, %s, %s)",
                        (album_counter, album_name, artist_id))
            # album_counter += 1
            return album_counter
        else:
            return cur.fetchone()[0]


def insert_new_song_lfm(con, title, artist_id, album_id, song_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT song_id FROM songs WHERE name = %s AND artist_id = %s",
                    (title, artist_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO songs (song_id, name, album_id, artist_id) VALUES(%s, %s, %s, %s)",
                        (song_counter, title, album_id, artist_id))
            # song_counter += 1
            return song_counter
        else:
            return cur.fetchone()[0]


def get_tracks_last_fm():
    network = pylast.LastFMNetwork(api_key=LFM_API_KEY, api_secret=LFM_API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "mr_music")
    chart_songs = network.get_top_tracks(1000)
    artist_counter = 0
    album_counter = 0
    song_counter = 0
    for song in chart_songs:
        artist, title = get_title_and_artist_from_item(str(song.item))
        artist_id = insert_new_artist_lfm(con, artist, artist_counter)
        # try:
        #     track = network.get_track(artist, title)
        #     if track is not None and track.get_album() is not None:
        #         album_id = insert_new_album(con, track.get_album().get_name(), artist_id, album_counter)
        #     else:
        #         album_id = insert_new_album(con, "unknown", artist_id, album_counter)
        #     song_counter = insert_new_song(con, title, artist_id, album_id, song_counter)
        # except pylast.NetworkError:
        #     song_counter = insert_new_song(con, title, artist_id, -1, song_counter)
        insert_new_song_lfm(con, title, artist_id, -1, song_counter)
        artist_counter += 1
        album_counter += 1
        song_counter += 1


def insert_new_artist_mm_by_id(con, artist_id, artist_name, rating, country):
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM artists WHERE artist_id = %s", artist_id)
            if cur.rowcount == 0:
                cur.execute("INSERT INTO artists (artist_id, name, rating, country) VALUES(%s, %s, %s, %s)",
                            (artist_id, artist_name, rating, country))
                print 'added: ' + artist_name
    except:
        pass


def insert_new_album_mm(con, album_id, name, artist_id, cover, year, month, album_type, mbid, rating=-1):
    try:
        with con:
            cur = con.cursor()
            cur.execute("SELECT album_id FROM albums WHERE album_id = %s", album_id)
            if cur.rowcount == 0:
                cur.execute(
                    "INSERT INTO albums (album_id, name, rating, artist_id, cover, release_year, release_month, type, album_mbid) VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s)",
                    (album_id, name, rating, artist_id, cover, year, month, album_type, mbid))
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


def get_missing_artists():
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    set_of_artists = set()

    with con:
        cur = con.cursor()
        cur.execute("SELECT DISTINCT song_name, artist_name FROM popular_songs WHERE song_id = -1 GROUP BY artist_name")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            song_name, artist_name = row[0], row[1]
            set_of_artists.add((song_name, artist_name))
    for song_name, artist_name in set_of_artists:
        try:
            search = musixmatch.matcher_track_get(song_name, artist_name)
            artist_id = search.get('message').get('body').get('track').get('artist_id')
            artist = musixmatch.artist_get(artist_id).get('message').get('body').get('artist')
            artist_country = artist.get('artist_country')
            artist_rating = artist.get('artist_rating')
            insert_new_artist_mm_by_id(con, artist_id, artist_name, artist_rating, artist_country)
            # artist_name = artist_name.encode('utf-8')
            # message = musixmatch.artist_search(artist_name, 1, 1, 0, 0).get('message')
            # artist_list = message.get('body').get('artist_list')
            # if artist_list:  # not empty
            #     artist = artist_list.pop().get('artist')
            #     artist_id = artist.get('artist_id')
            #     country = artist.get('artist_country')
            #     rating = artist.get('artist_rating')
            #     insert_new_artist_mm_by_id(con, artist_id, artist_name, rating, country)
        except Exception as e:
            print "error occurred: artist_name = " + artist_name
            print e.message


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
                insert_new_artist_mm_by_id(con, artist_name, artist_id)
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
                release_date = album.get('album_release_date')
                release_date = release_date.split('-')
                year = -1
                month = -1
                if len(release_date) > 0:
                    year = release_date[0]
                    if len(release_date) > 1:
                        month = release_date[1]
                album_type = album.get('album_release_type')
                album_mbid = album.get('album_mbid')
                insert_new_album_mm(con, album_id, album_name, artist_id, album_cover, year, month, type,
                                    album_mbid, rating)


def get_all_albums_from_artists(list_of_artists):
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        for artist in list_of_artists:
            cur.execute("SELECT artist_id FROM artists WHERE name = %s", artist)
            list_of_lists_of_albums = list()
            for i in range(cur.rowcount):
                artist_id = cur.fetchone()[0]
                for j in range(1, 5):
                    list_of_lists_of_albums.append(
                        musixmatch.artist_albums_get(artist_id, 1, j, 100, 'desc').get('message').get('body').get(
                            'album_list'))
            for list_of_albums in list_of_lists_of_albums:
                for album in list_of_albums:
                    album = album.get('album')
                    artist_id = album.get('artist_id')
                    album_id = album.get('album_id')
                    album_name = album.get('album_name')
                    rating = album.get('album_rating')
                    album_cover = album.get('album_coverart_100x100')
                    release_date = album.get('album_release_date')
                    release_date = release_date.split('-')
                    year = -1
                    month = -1
                    if len(release_date) > 0:
                        year = release_date[0]
                        if len(release_date) > 1:
                            month = release_date[1]
                    album_type = album.get('album_release_type')
                    album_mbid = album.get('album_mbid')
                    insert_new_album_mm(con, album_id, album_name, artist_id, album_cover, year, month, album_type,
                                        album_mbid, rating)
        print 'done inserting albums for artist: ' + artist


def insert_new_tracks_from_list(con, list_of_lists_of_songs):
    for lst in list_of_lists_of_songs:
        for song in lst:
            song = song.get('track')
            song_id = song.get('track_id')
            title = song.get('track_name')
            lyrics_id = song.get('lyrics_id')
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


def get_all_tracks_from_albums_by_artists(list_of_artists):
    musixmatch = Musixmatch(MM_API_KEY)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        for artist in list_of_artists:
            list_of_lists_of_songs = list()
            try:
                cur.execute(
                    "SELECT album_id, album_mbid FROM albums WHERE album_mbid IS NOT NULL AND artist_id = (SELECT artist_id FROM artists WHERE name = %s)",
                    artist)
                for i in range(cur.rowcount):
                    row = cur.fetchone()
                    album_id, album_mbid = row[0], row[1]
                    ll = musixmatch.album_tracks_get(album_id, 1, 100, album_mbid).get('message')
                    list_of_lists_of_songs.append(ll.get('body').get('track_list'))

            except Exception as e:
                print "error occurred: "
                print e.message
                print "size of list of lists: " + str(len(list_of_lists_of_songs))
            insert_new_tracks_from_list(con, list_of_lists_of_songs)
            print 'done inserting songs from artist: ' + artist


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
            cur.execute("SELECT * FROM lyrics WHERE song_id = %s", song_id)
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
            cur.execute("SELECT song_id FROM popular_songs")
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


def insert_popular_song_to_table(con, country, song_name, artist_name, playcount, album_cover):
    with con:
        cur = con.cursor()
        cur.execute('SET CHARACTER SET utf8')
        cur.execute('SET character_set_connection=utf8')
        cur.execute(
            "SELECT * FROM popular_songs WHERE country_name = %s AND song_name = %s AND artist_name = %s",
            (country, song_name, artist_name))
        if cur.rowcount == 0:
            try:
                cur.execute(
                    "INSERT INTO popular_songs (country_name, song_name, artist_name, playcount, album_cover) VALUES(%s, %s, %s, %s,%s)",
                    (country, song_name, artist_name, playcount, album_cover))
            except Exception as e:
                print "error occurred: couldn't insert song name: " + song_name
                print e.message


def get_album_covers_for_all_albums():
    network = pylast.LastFMNetwork(api_key=LFM_API_KEY, api_secret=LFM_API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        cur.execute('SELECT album_mbid FROM albums WHERE cover = %s', ('http://s.mxmcdn.net/images-storage/albums/nocover.png'))
        dict_of_covers = dict()
        for i in range(cur.rowcount):
            try:
                album_mbid = cur.fetchone()[0]
                if album_mbid != '':
                    album_cover = network.get_album_by_mbid(album_mbid).get_cover_image()
                    dict_of_covers.update({album_mbid: album_cover})
            except Exception as e:
                print "error occurred: "
                print e.message
                print 'size of dict: ' + str(len(dict_of_covers))
                # update_album_covers_with_mbid(cur, dict_of_covers)
                # dict_of_covers.clear()
        update_album_covers_with_mbid(cur, dict_of_covers)


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


def update_popular_songs(cur, dict_of_updates_popular):
    for song_name, artist_name in dict_of_updates_popular:
        song_id = dict_of_updates_popular[(song_name, artist_name)]
        cur.execute(
            "UPDATE popular_songs SET song_id = %s WHERE song_name = %s AND artist_name = %s",
            (song_id, song_name, artist_name))


def get_song_ids_from_db():
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    musixmatch = Musixmatch(MM_API_KEY)
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT DISTINCT song_name, artist_name, artist_id FROM popular_songs, artists WHERE popular_songs.artist_name = artists.name AND song_id = -1")
        set_of_new_songs = set()
        dict_of_updates_popular = dict()
        for i in range(cur.rowcount):
            row = cur.fetchone()
            song_name, artist_name, artist_id = row[0], row[1], row[2]
            set_of_new_songs.add((song_name, artist_name, artist_id))
        for song_name, artist_name, artist_id in set_of_new_songs:
            cur.execute(
                "SELECT song_id FROM songs WHERE title = %s AND artist_id = %s", (song_name, artist_id))
            if cur.rowcount > 0:
                song_id = cur.fetchone()[0]
                dict_of_updates_popular.update({(song_name, artist_name): song_id})
            else:
                try:
                    message = musixmatch.matcher_track_get(song_name, artist_name).get('message')
                    if message.get('header').get('status_code') == 200:
                        track = message.get('body').get('track')
                        song_id = track.get('track_id')
                        lyrics_id = track.get('lyrics_id')
                        album_id = track.get('album_id')
                        rating = track.get('track_rating')
                        insert_new_song_mm(con, song_id, song_name, lyrics_id, album_id, artist_id, rating)
                except Exception as e:
                    print "error occurred: couldn't get song " + song_name
                    print e.message
        update_popular_songs(cur, dict_of_updates_popular)


def update_album_covers_with_mbid(cur, dict_of_covers):
    for album_mbid in dict_of_covers:
        album_cover = dict_of_covers[album_mbid]
        cur.execute('SELECT * FROM albums WHERE album_mbid = %s AND cover != %s', (album_mbid, 'http://s.mxmcdn.net/images-storage/albums/nocover.png'))
        if cur.rowcount == 0:
            cur.execute("UPDATE albums SET cover = %s WHERE album_mbid = %s", (album_cover, album_mbid))


def update_album_covers(cur, dict_of_covers):
    for album_id in dict_of_covers:
        album_cover = dict_of_covers[album_id]
        cur.execute('SELECT * FROM albums WHERE album_id = %s AND cover != %s', (album_id, 'http://s.mxmcdn.net/images-storage/albums/nocover.png'))
        if cur.rowcount == 0:
            cur.execute("UPDATE albums SET cover = %s WHERE album_id = %s", (album_cover, album_id))


def update_album_types(cur, dict_of_types):
    for album_id in dict_of_types:
        album_type = dict_of_types[album_id]
        cur.execute('SELECT * FROM albums WHERE album_id = %s', album_id)
        if cur.rowcount == 0:
            cur.execute("UPDATE albums SET type = %s", album_type)


def fix_album_types():
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    musixmatch = Musixmatch(MM_API_KEY)
    dict_of_types = dict()
    with con:
        cur = con.cursor()
        cur.execute('SELECT album_id FROM albums WHERE type = %s', '<type \'type\'>')
        for i in range(cur.rowcount):
            try:
                album_id = cur.fetchone()[0]
                message = musixmatch.album_get(album_id).get('message')
                if message.get('header').get('status_code') == 200:
                    album = message.get('body').get('album')
                    album_type = album.get('album_release_type')
                    dict_of_types.update({album_id: album_type})
                else:
                    print 'received code :' + str(message.get('header').get('status_code'))
            except Exception as e:
                print "error occurred: couldn't get album " + str(album_id)
                print e.message
        update_album_types(cur, dict_of_types)


def get_album_covers_from_popular():
    con = mdb.connect('localhost', 'root', 'Armageddon1', "musixmatch")
    with con:
        cur = con.cursor()
        dict_of_covers = dict()
        cur.execute('SELECT album_id, album_cover FROM songs, popular_songs WHERE songs.song_id = popular_songs.song_id')
        for i in range(cur.rowcount):
            row = cur.fetchone()
            album_id, album_cover = row[0], row[1]
            dict_of_covers.update({album_id: album_cover})
        update_album_covers(cur, dict_of_covers)


if __name__ == '__main__':
    get_album_covers_for_all_albums()
    # get_album_covers_from_popular()
    # fix_album_types()                                  # NEED TO DO THIS
    # get_song_ids_from_db()
    # get_tracks_musixmatch()
    # get_artist_ratings()
    # get_album_ratings()
    # get_all_albums_from_artists()
    # get_release_dates_albums_and_types()
    # get_mbid_from_albums()
    # get_all_tracks_from_albums()
    # get_lyrics_of_tracks()
    # get_lyrics_translation()
    # get_top_tracks_by_country("United Kingdom", 200)
    # get_missing_artists()
    # lst = {'The Weekend'}
    # get_all_albums_from_artists(lst)
    # get_all_tracks_from_albums_by_artists(lst)
