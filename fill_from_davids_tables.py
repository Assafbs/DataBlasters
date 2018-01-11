#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import re


def print_header(header):
    print '-' * 30, " ", header, " ", '-' * 35


def get_albums_sql(row):
    return "INSERT INTO DbMysql09.albums VALUES({}, {}, {}, {}, {}, {}, {})".format(
        sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]), sql_esc(row[3]), sql_esc(row[4]),
        sql_month_esc(row[5]), sql_esc(row[6]))


def get_songs_sql(row):
    if not ("(" in row[1]):
        return "INSERT INTO DbMysql09.songs VALUES({}, {}, {}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]), sql_esc(row[3]))
    else:
        return "dropped " + row[1]


def get_artists_sql(row):
    # if not("&" in row[1] or "feat." in row[1] or " and " in row[1]):
    return "INSERT INTO DbMysql09.artists VALUES({}, {}, {})".format(
              sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]))


def get_performed_by_sql(row):
    return "INSERT INTO dbmysql09.performed_by VALUES({}, {})".format(
                sql_esc(row[0]), sql_esc(row[1]))


def get_lyrics_sql(row):
    return "INSERT INTO DbMysql09.lyrics VALUES({}, {}, {}, {})".format(
            sql_esc(row[0]), sql_lyrics_esc(row[1]), sql_esc(row[2]), sql_lyrics_esc(row[3]))


def get_popular_by_country_sql(row):
    return "INSERT INTO DbMysql09.popular_songs_by_country VALUES({}, {}, {})".format(
            sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]))


def fill_table(get_sql, select):
    # david_con = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="david")
    mydbcon = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")
    mycon = mdb.connect(host="localhost", user="DbMysql09", passwd="DbMysql09", db="DbMysql09", port=3305)

    # david_cur = david_con.cursor()
    david_cur = mycon.cursor()
    mycur = mydbcon.cursor()
    my_2_cur = mydbcon.cursor()

    # david_con.set_character_set('utf8')
    # david_cur.execute('SET CHARACTER SET utf8')
    # david_cur.execute('SET character_set_connection=utf8')
    # mycon.set_character_set('utf8')
    # mycur.execute('SET CHARACTER SET utf8')
    # mycur.execute('SET character_set_connection=utf8')

    david_cur.execute(select)
    row = david_cur.fetchone()
    bad = 0
    while row is not None:
        try:
            names = re.split(' & | feat. ', row[2])
            count = 0
            # if 2 or more artists exist enter them
            for name in names:
                sql_select = "SELECT artists.artist_id, artists.name FROM dbmysql09.artists WHERE artists.name = {}".format(sql_esc(name))
                my_2_cur.execute(sql_select)
                row_2 = my_2_cur.fetchone()
                if row_2 is not None:
                    count = count + 1
                    if count == 1:
                        old = row_2
                    elif count > 1:
                        print "enter " + old[1] + " from " + row[2]
                        mycur.execute(get_sql((row[0], row_2[0])))
                        if count == 2:
                            print "enter " + name + " from " + row[2]
                            mycur.execute(get_sql((row[0], old[0])))
                else:
                    print name + " is not in db"
            row = david_cur.fetchone()

        except Exception as e:
            print row
            print(get_sql(row))
            print e
            row = david_cur.fetchone()
            pass

    # david_cur.close()
    # david_con.close()

    mycur.close()
    mydbcon.commit()
    mydbcon.close()
    mycon.close()


def get_artists():
    print_header("getting_artists")
    select = "SELECT artist_id, name, country FROM david.artists"
    fill_table(get_artists_sql, select)


def get_albums():
    print_header("getting_albums")
    select = "SELECT album_id, name, artist_id, cover, release_year, release_month, type FROM david.albums"
    fill_table(get_albums_sql, select)


def get_songs():
    print_header("getting_songs")
    select = "SELECT song_id, title, album_id, rating FROM david.songs WHERE songs.title not like '%(%'"
    fill_table(get_songs_sql, select)


def get_performed_by():
    print_header("getting performed by")
    # select = ("SELECT song_id, songs.artist_id, artists.name FROM david.songs "
    #           "JOIN david.artists ON songs.artist_id=artists.artist_id "
    #           "WHERE artists.name not like '%&%' and artists.name not like '%Feat%' and artists.name not like '% and %'")


    select = ("SELECT songs.song_id, artists.artist_id FROM DbMysql09.songs "
              "JOIN DbMysql09.albums ON songs.album_id=albums.album_id "
              "JOIN DbMysql09.artists ON albums.artist_id=artists.artist_id "
              "WHERE artists.name not like '%&%' and artists.name not like '%Feat%' and artists.name not like '% and %'")
    fill_table(get_performed_by_sql, select)


def get_performed_by_split():
    print_header("getting performed by")

    select = ("SELECT songs.song_id, artists.artist_id, artists.name FROM DbMysql09.songs "
              "JOIN DbMysql09.albums ON songs.album_id=albums.album_id "
              "JOIN DbMysql09.artists ON albums.artist_id=artists.artist_id "
              "WHERE artists.name like '%&%' or artists.name like '%Feat%' or artists.name like '% and %'")
    fill_table(get_performed_by_sql, select)

def get_lyrics():
    print_header("getting lyrics")
    select = "SELECT song_id, text, src_lang, translation FROM david.lyrics WHERE text<>''"
    fill_table(get_lyrics_sql, select)


def get_popular_by_country():
    print_header("getting popular by country")
    select = "SELECT country_name, song_id, playcount  FROM david.popular_songs"
    fill_table(get_popular_by_country_sql, select)


def sql_esc(s):
    if s is None:
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


def sql_lyrics_esc(s):

    if s is None:
        return mdb.NULL
    else:
        s = '\n'.join(s.split('\n')[:-2])
        return "'" + str(s).replace("'", "''") + "'"


def sql_month_esc(s):
    if s is None or s < 1:
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


if __name__ == '__main__':
    # get_artists()
    # get_albums()
    # get_songs()
    # get_lyrics()
    # get_performed_by()
    get_performed_by_split()
    # get_popular_by_country()
    print_header("finish")
