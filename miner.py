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


def insert_new_artist(con, artist_name, artist_counter):
    with con:
        cur = con.cursor()
        cur.execute("SELECT artist_id FROM artists WHERE name = %s", artist_name)
        if cur.rowcount == 0:
            cur.execute("INSERT INTO artists (artist_id, name) VALUES(%s, %s)", (artist_counter, artist_name))
            # artist_counter += 1
            return artist_counter
        else:
            return cur.fetchone()[0]


def insert_new_album(con, album_name, artist_id, album_counter):
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


def insert_new_song(con, title, artist_id, album_id, song_counter):
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
        artist_id = insert_new_artist(con, artist, artist_counter)
        # try:
        #     track = network.get_track(artist, title)
        #     if track is not None and track.get_album() is not None:
        #         album_id = insert_new_album(con, track.get_album().get_name(), artist_id, album_counter)
        #     else:
        #         album_id = insert_new_album(con, "unknown", artist_id, album_counter)
        #     song_counter = insert_new_song(con, title, artist_id, album_id, song_counter)
        # except pylast.NetworkError:
        #     song_counter = insert_new_song(con, title, artist_id, -1, song_counter)
        insert_new_song(con, title, artist_id, -1, song_counter)
        artist_counter += 1
        album_counter += 1
        song_counter += 1


def get_tracks_musixmatch():
    try:
        musixmatch = Musixmatch(MM_API_KEY)
        chart = musixmatch.chart_tracks_get(1, 2, 3)

        print chart
    except:
        pass


if __name__ == '__main__':
    get_tracks_musixmatch()
