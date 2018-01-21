import MySQLdb as mdb


def sql_esc(s):
    if s is None: # or s == "<type 'type'>":
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


def sql_month_esc(s):
    if s is None or s < 1:
        return mdb.NULL
    else:
        return "'" + str(s).replace("'", "''") + "'"


def transfer_artists(nova_con, nova_cur, fin_cur):

    select = "select artist_id, artist_name, country_name from dbmysql09.artists"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    while row is not None:
        try:
            insert = "INSERT INTO DbMysql09.artists VALUES({}, {}, {})".format(
                sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]))
            nova_cur.execute(insert)
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def transfer_albums(nova_con, nova_cur, db_cur):
    select = "SELECT album_id, album_name, artist_id, albums_cover, release_year, release_month, type FROM dbmysql09.albums"
    db_cur.execute(select)
    row = db_cur.fetchone()

    count = 0
    while row is not None:
        if count%500 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO albums VALUES({}, {}, {}, {}, {}, {}, {})".format(
                sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]), sql_esc(row[3]), sql_esc(row[4]),
                sql_month_esc(row[5]), sql_esc(row[6]))
            nova_cur.execute(insert)
            count += 1
            row = db_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = db_cur.fetchone()
            pass

    nova_con.commit()


def transfer_songs(nova_con, nova_cur, fin_cur):
    select = "SELECT songs.song_id, title, album_id, rank FROM dbmysql09.songs"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    count = 0
    while row is not None:
        if count % 500 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO DbMysql09.songs VALUES({}, {}, {}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]), sql_esc(row[3]))
            nova_cur.execute(insert)
            count += 1
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def transfer_lyrics(nova_con, nova_cur, fin_cur):
    nova_con.set_character_set('utf8')
    fin_cur.execute('SET CHARACTER SET utf8')
    fin_cur.execute('SET character_set_connection=utf8')
    nova_cur.execute('SET CHARACTER SET utf8');
    nova_cur.execute("SET character_set_client=utf8");
    nova_cur.execute("SET character_set_connection=utf8");
    nova_cur.execute("SET character_set_database=utf8");
    nova_cur.execute("SET character_set_results=utf8");
    nova_cur.execute("SET character_set_server=utf8");

    select = "SELECT song_id, lyrics, lyrics_language, hebrew_translation FROM dbmysql09.lyrics"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    count = 0
    while row is not None:
        if count%100 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO DbMysql09.lyrics VALUES({}, {}, {}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]), sql_esc(row[3]))
            nova_cur.execute(insert)
            count += 1
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def transfer_popular(nova_con, nova_cur, fin_cur):
    select = "SELECT country_name, song_id, rank FROM dbmysql09.popular_songs_by_country"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    count = 0
    while row is not None:
        if count%100 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO DbMysql09.popular_songs_by_country VALUES({}, {}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]), sql_esc(row[2]))
            nova_cur.execute(insert)
            count+=1
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def transfer_performed_by(nova_con, nova_cur, fin_cur):
    select = "SELECT song_id, artist_id FROM dbmysql09.performed_by"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    count = 0
    while row is not None:
        if count%100 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO DbMysql09.performed_by VALUES({}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]))
            nova_cur.execute(insert)
            count+=1
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def transfer_frequent_words(nova_con, nova_cur, fin_cur):
    select = "SELECT word, frequency FROM dbmysql09.frequent_words"
    fin_cur.execute(select)
    row = fin_cur.fetchone()

    count = 0
    while row is not None:
        if count%100 == 0:
            nova_con.commit()
            print count
        try:
            insert = "INSERT INTO DbMysql09.frequent_words VALUES({}, {})".format(
                    sql_esc(row[0]), sql_esc(row[1]))
            nova_cur.execute(insert)
            count+=1
            row = fin_cur.fetchone()

        except Exception as e:
            print row
            print insert
            print e
            row = fin_cur.fetchone()
            pass

    nova_con.commit()


def print_header(header):
    print '-' * 30, " ", header, " ", '-' * 35


if __name__ == '__main__':

    nova_con = mdb.connect(host="localhost", user="DbMysql09", passwd="DbMysql09", db="DbMysql09", port=3305)
    nova_cur = nova_con.cursor()

    db_con = mdb.connect(host="localhost", user="root", passwd="Tahan049", db="dbmysql09")
    db_cur = db_con.cursor()

    # transfer our local DB to nova

    # transfer_artists(nova_con,nova_cur, db_cur)
    # transfer_albums(nova_con,nova_cur, db_cur)
    # transfer_songs(nova_con,nova_cur, db_cur)
    # transfer_lyrics(nova_con,nova_cur, db_cur)
    # transfer_popular(nova_con,nova_cur, db_cur)
    # transfer_performed_by(nova_con,nova_cur, db_cur)
    # transfer_frequent_words(nova_con,nova_cur, db_cur)

    print_header("finish")

    nova_con.commit()
    nova_cur.close()
    db_cur.close()
    db_con.close()
    nova_con.close()




