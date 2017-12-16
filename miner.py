import pylast
import MySQLdb as mdb

API_KEY = "d202d3c8b0726f003b32954d7d37e6ab"
API_SECRET = "186006795c45cabe0d4692cd8dd6b01c"

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
        cur.execute("SELECT song_id FROM songs WHERE name = %s AND artist_id = %s AND album_id = %s",
                    (title, artist_id, album_id))
        if cur.rowcount == 0:
            cur.execute("INSERT INTO songs (song_id, name, album_id, artist_id) VALUES(%s, %s, %s, %s)",
                        (song_counter, title, album_id, artist_id))
            # song_counter += 1
            return song_counter
        else:
            return cur.fetchone()[0]


def get_tracks():
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=username, password_hash=password_hash)
    con = mdb.connect('localhost', 'root', 'Armageddon1', "mr_music")
    chart_songs = network.get_top_tracks(20000)
    artist_counter = 0
    album_counter = 0
    song_counter = 0
    for song in chart_songs:
        artist, title = get_title_and_artist_from_item(str(song.item))
        track = network.get_track(artist, title)
        artist_counter = insert_new_artist(con, artist, artist_counter)
        if track is not None and track.get_album() is not None:
            album_counter = insert_new_album(con, track.get_album().get_name(), artist_counter, album_counter)
        else:
            album_counter = insert_new_album(con, "unknown", artist_counter, album_counter)
        song_counter = insert_new_song(con, title, artist_counter, album_counter, song_counter)
        artist_counter += 1
        album_counter += 1
        song_counter += 1


if __name__ == '__main__':
    get_tracks()
