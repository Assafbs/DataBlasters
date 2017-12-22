import MySQLdb as mdb
import pylast
from musixmatch import Musixmatch

LFM_API_KEY = "d202d3c8b0726f003b32954d7d37e6ab"
LFM_API_SECRET = "186006795c45cabe0d4692cd8dd6b01c"
MM_API_KEY = "3dbef1b0188814ddcc0f7bdd95ed9902"

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
        cur.execute("SELECT artist_id FROM artists")
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
        cur.execute("SELECT album_id FROM albums")
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
            chart = musixmatch.chart_tracks_get(i, 100, 0)
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
            cur.execute("SELECT album_id FROM albums WHERE type = 'Album' OR type = 'Compilation' OR type = 'EP'")
            for i in range(cur.rowcount):
                album_id = cur.fetchone()[0]
                list_of_lists_of_songs.append(
                    musixmatch.album_tracks_get(album_id, 1, 1, 100).get('message').get('body').get('track_list'))
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


if __name__ == '__main__':
    # get_tracks_musixmatch()
    # get_artist_ratings()
    # get_album_ratings()
    # get_all_albums_from_artists()
    # get_release_dates_albums_and_types()
    get_all_tracks_from_albums()
