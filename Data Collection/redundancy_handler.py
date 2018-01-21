import string
import re
from difflib import SequenceMatcher
import MySQLdb as mdb
import pickle
# -*- coding: latin-1 -*-


class RedundancyHandler:

    def __init__(self):
        pass

    @staticmethod
    def areSimilar(word1, word2, minimal_similarity):
        # Make them lower case.
        word1 = word1.lower()
        word2 = word2.lower()
        # Remove brackets
        word1 = re.sub(r'\(.*\)', '', word1)
        word2 = re.sub(r'\(.*\)', '', word2)
        word1 = re.sub(r'\[.*\]', '', word1)
        word2 = re.sub(r'\[.*\]', '', word2)
        word1 = re.sub(r'\{.*\}', '', word1)
        word2 = re.sub(r'\{.*\}', '', word2)
        # Remove punctuation.
        word1 = word1.translate(None, string.punctuation)
        word2 = word2.translate(None, string.punctuation)
        # Remove redundant spaces.
        word1 = re.sub(' +', ' ', word1)
        word2 = re.sub(' +', ' ', word2)
        # Remove whitespaces from start/end.
        word1 = word1.strip()
        word2 = word2.strip()
        # Check if similarity is above the given threshold.
        return SequenceMatcher(None, word1, word2).ratio() > minimal_similarity


def sql_type_esc(s):
    if s is None or "type" in s:
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


def sql_esc(s):
    if s is None :
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


def sql_month_esc(s):
    if s is None or s < 1 or s>12:
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


# split artists that perform together
# i.e. & feat. and into single artist
def split_artists():

    fin_con = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")

    orig_cur = fin_con.cursor()
    my_2_cur = fin_con.cursor()
    fin_cur = fin_con.cursor()

    select = ("SELECT songs.song_id, artists.artist_id, artists.artist_name FROM dbmysql09.songs "
              "JOIN dbmysql09.artists ON songs.artist_id=artists.artist_id "
              "WHERE artists.artist_name like '%&%' or artists.artist_name like '%Feat%' or artists.artist_name like '% and %'")

    orig_cur.execute(select)
    row = orig_cur.fetchone()
    # get max id - updated before run
    max_id = 35003833
    while row is not None:
        try:
            # split artist name into single artist
            names = re.split(' & | feat. | feat.| Feat. | fEAT. |, ', row[2])
            for name in names:
                try:
                    # check if artist is in our data base
                    sql_select = "SELECT artists.artist_id, artists.artist_name FROM dbmysql09.artists WHERE artists.artist_name = {}".format(sql_esc(name))
                    my_2_cur.execute(sql_select)
                    row_2 = my_2_cur.fetchone()
                    if row_2 is None:
                        # if not in DB enter new artist
                        insert_artist = "INSERT INTO dbmysql09.artists VALUES({}, {}, {})".format(
                            sql_esc(max_id), sql_esc(name), mdb.NULL)
                        print(insert_artist)
                        fin_cur.execute(insert_artist)
                        max_id += 1
                        print "create new artist " + name
                        print max_id

                        # enter new perfomed_by row[song],new_artisit
                        insert = "INSERT INTO dbmysql09.performed_by VALUES({}, {})".format(
                            sql_esc(row[0]), sql_esc(row[1]))

                        print "from " + row[2]
                        print "- " * 20
                    else:
                        #  enter new perfomed_by song, found artist
                        insert = "INSERT INTO dbmysql09.performed_by VALUES({}, {})".format(
                                 sql_esc(row[0]), sql_esc(row_2[0]))
                        print("old artist " +row_2[1])
                        print "from " + row[2]
                        print "* " * 20

                    fin_cur.execute(insert)

                except Exception as e:
                    print row
                    print(insert)
                    print e
                    row = orig_cur.fetchone()
                    pass
            row = orig_cur.fetchone()

        except Exception as e:
            print row
            print e
            row = orig_cur.fetchone()
            pass

    fin_con.commit()
    orig_cur.close()
    my_2_cur.close()
    fin_cur.close()
    fin_con.close()


def pickle_to_table():
    print("start")
    # pickle created for the frequent_words table
    # creating pickle code is in WordInSongs
    newfile= 'frqWordCountDict.pickle'
    with open(newfile, 'rb') as fwcd:
        dictionary = pickle.load(fwcd)

    con = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")
    cur = con.cursor()

    for key in dictionary:
        val = dictionary[key]
        insert = "INSERT INTO dbmysql09.frequent_words VALUES({}, {})".format(
                    sql_esc(key), sql_esc(val))
        try:
            cur.execute(insert)
        except Exception as e:
            print(insert)
            print e
            pass

    con.commit()
    cur.close()
    con.close()

# remove duplicate lyrics by comparing the first line in the song
def remove_lyrics():
    mycon = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")

    mid_cur = mycon.cursor()
    mid_cur2 = mycon.cursor()
    mid_cur3 = mycon.cursor()

    mid_cur.execute("SELECT song_id, lyrics FROM dbmysql09.lyrics")
    row = mid_cur.fetchone()
    cnt =0
    while row is not None:
        print cnt
        cnt += 1
        try:
            dup = False
            mid_cur2.execute(
                "SELECT song_id, lyrics FROM dbmysql09.lyrics where lyrics.song_id <> {} ".format(
                    row[0]))
            row2 = mid_cur2.fetchone()
            while row2 is not None:
                try:
                    row_song1 = (row[1].split('\n')[0])
                    row_song2 = (row2[1].split('\n')[0])
                    if RedundancyHandler.areSimilar(row_song1, row_song2, 0.9):
                        print("found duplicates")
                        print(row_song1)
                        print(row_song2)
                        print("-" * 20)

                        delete = "DELETE FROM dbmysql09.lyrics where song_id = {}".format(row2[0])
                        mid_cur3.execute(delete)
                        mycon.commit()
                        break
                    row2 = mid_cur2.fetchone()

                except Exception as e:
                    print row
                    print row2
                    print delete
                    print e
                    row2 = mid_cur2.fetchone()
                    pass
            row = mid_cur.fetchone()


        except Exception as e:
            print row
            print e
            row = mid_cur.fetchone()
            pass

    mycon.commit()
    mid_cur.close()
    mid_cur2.close()
    mid_cur3.close()
    mycon.close()


# remove duplicate songs by comparing the title of a song
# with all the songs from the same artist
def remove_songs():
    mycon = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")

    mid_cur = mycon.cursor()
    mid_cur2 = mycon.cursor()
    mid_cur3 = mycon.cursor()

    mid_cur.execute("SELECT song_id, title, artist_id FROM dbmysql09.songs")
    row = mid_cur.fetchone()
    cnt =0
    while row is not None:
        print cnt
        cnt += 1
        try:
            mid_cur2.execute(
                "SELECT song_id, title FROM dbmysql09.songs where song_id < {} and artist_id = {} ".format(
                    row[0], row[2]))
            row2 = mid_cur2.fetchone()
            while row2 is not None:
                try:
                    if RedundancyHandler.areSimilar(row[1], row2[1], 0.9):
                        print("found duplicates")
                        print(row[1])
                        print(row2[1])
                        print("-" * 20)

                        delete = "DELETE FROM dbmysql09.songs where song_id = {}".format(row2[0])
                        mid_cur3.execute(delete)
                        mycon.commit()
                        break
                    row2 = mid_cur2.fetchone()

                except Exception as e:
                    print row
                    print row2
                    print delete
                    print e
                    row2 = mid_cur2.fetchone()
                    pass
            row = mid_cur.fetchone()


        except Exception as e:
            print row
            print e
            row = mid_cur.fetchone()
            pass

    mycon.commit()
    mid_cur.close()
    mid_cur2.close()
    mid_cur3.close()
    mycon.close()


# remove duplicate albums by comparing the name of an album
# with all the albums from the same artist
def remove_albums():
    mycon = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")

    mid_cur = mycon.cursor()
    mid_cur2 = mycon.cursor()
    mid_cur3 = mycon.cursor()

    mid_cur.execute("SELECT album_id, album_name, artist_id FROM dbmysql09.albums")
    row = mid_cur.fetchone()
    cnt =0
    while row is not None:
        print cnt
        cnt += 1
        try:
            dup = False
            # get albums from same artist
            mid_cur2.execute(
                "SELECT album_id, album_name FROM dbmysql09.albums where albums.album_id < {} and artist_id = {} ".format(
                    row[0], row[2]))
            row2 = mid_cur2.fetchone()
            while row2 is not None:
                try:
                    if RedundancyHandler.areSimilar(row[1], row2[1], 0.9):
                        print("found duplicates")
                        print(row[1])
                        print(row2[1])
                        print("-" * 20)

                        delete = "DELETE FROM dbmysql09.albums where album_id = {}".format(row2[0])
                        mid_cur3.execute(delete)
                        mycon.commit()
                        break
                    row2 = mid_cur2.fetchone()

                except Exception as e:
                    print row
                    print row2
                    print delete
                    print e
                    row2 = mid_cur2.fetchone()
                    pass
            row = mid_cur.fetchone()

        except Exception as e:
            print row
            print e
            row = mid_cur.fetchone()
            pass

    mycon.commit()
    mid_cur.close()
    mid_cur2.close()
    mid_cur3.close()
    mycon.close()


def print_header(header):
    print '-' * 30, " ", header, " ", '-' * 35


if __name__ == '__main__':
    # pickle_to_table()
    # split_artists()
    # remove_lyrics()
    # remove_songs()
    # remove_albums()
    print_header("finish")










