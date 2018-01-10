import time


class QueryGenerator:

    def __init__(self):
        pass

    @staticmethod
    def create_score_update_query(nickname, game_id, score):
        return """INSERT INTO scores (nickname, date, game_id, score) VALUES (%s, %s, %s, %s)""", (nickname, time.strftime('%Y-%m-%d %H:%M:%S'), game_id, score)

    @staticmethod
    def get_translated_song_question_query():
        return "SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.title\n" \
               "FROM lyrics JOIN songs ON lyrics.song_id = songs.song_id\n" \
               "WHERE lyrics.hebrew_translation IS NOT NULL\n" \
               "ORDER BY rand()\n" \
               "LIMIT 1"

    @staticmethod
    def get_translated_song_answers_query():
        return "SELECT DISTINCT songs.title, (count(*) - 1) AS numWords\n" \
               "FROM songs JOIN (\n" \
               "(SELECT song_id \n" \
               "FROM lyrics\n" \
               "WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n" \
               "UNION ALL\n" \
               "(SELECT song_id \n" \
               "FROM lyrics \n" \
               "WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n" \
               "UNION ALL\n" \
               "(SELECT song_id \n" \
               "FROM lyrics \n" \
               "WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n" \
               "UNION ALL\n" \
               "(SELECT song_id \n" \
               "FROM lyrics\n" \
               "WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n" \
               "UNION ALL\n" \
               "(SELECT song_id \n" \
               "FROM lyrics\n" \
               "WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n" \
               "UNION ALL \n" \
               "(SELECT song_id FROM lyrics)\n" \
               ") AS wordsCnt ON wordsCnt.song_id = songs.song_id\n" \
               "WHERE wordsCnt.song_id <> %s AND songs.title <> %s\n" \
               "GROUP BY wordsCnt.song_id\n" \
               "ORDER BY numWords DESC\n" \
               "LIMIT 3"

    @staticmethod
    def get_top_ten_query():
        return "SELECT nickname, SUM(total_per_game.final_score_per_game) AS final_score\n" \
               "FROM(SELECT total_per_game.nickname,total_per_game.game_id, (max_score + 10 *LOG2(total)) AS final_score_per_game\n" \
               "FROM (SELECT nickname, game_id, SUM(score) AS total\n" \
               "FROM musicdb.scores\n" \
               "GROUP BY nickname, game_id) AS total_per_game,\n" \
               "(SELECT nickname, game_id, MAX(score) AS max_score\n" \
               "FROM musicdb.scores\n" \
               "GROUP BY nickname, game_id) AS max_per_game\n" \
               "WHERE total_per_game.nickname = max_per_game.nickname\n" \
               "AND total_per_game.game_id = max_per_game.game_id) AS total_per_game\n" \
               "GROUP BY nickname\n" \
               "ORDER BY final_score DESC\n" \
               "LIMIT 10"

    @staticmethod
    def get_release_order_question_query():
        return """SELECT albums.album_id, albums.release_month, albums.release_year, songs.title\n
               FROM albums JOIN songs ON albums.album_id = songs.album_id\n
               WHERE release_month IS NOT NULL\n
               ORDER BY rand()\n
               LIMIT 1"""

    @staticmethod
    def get_release_order_answers_query():
        # TODO [tal]: maybe %s suppose to be %d here with number (otherwise it will add '') [David] No, it only works with %s

        return """SELECT monthDif, title\n
               FROM (\n
                    SELECT min(rowNum),  monthDif, title\n
                    FROM (\n
                        SELECT @n := @n + 1 rowNum, dateDist.*\n
                         FROM (SELECT @n:=0) initvars,\n
                              (SELECT IF(release_year = %s,\n
                                          abs(%s - release_month),\n
                                          IF (release_year > %s,\n
                                              release_month + (12 - %s) + 12*(release_year-(%s+1)),\n
                                              -(%s + (12 - release_month) + 12*(%s-(release_year+1)) )) ) AS monthDif,\n
                                          songs.title\n
                                FROM albums JOIN songs ON albums.album_id = songs.album_id\n
                                WHERE release_month IS NOT NULL AND albums.album_id <> %s\n
                                ORDER BY rand()) AS dateDist ) AS  dateDistWithNums\n
                    GROUP BY dateDistWithNums.monthDif \n
                    HAVING dateDistWithNums.monthDif <> 0\n
                    ORDER BY abs(dateDistWithNums.monthDif)\n
                    LIMIT 3 ) AS closestReleased\n
               ORDER BY closestReleased.monthDif"""

    @staticmethod
    def create_view_songs_by_artist(artist_id):
        return """CREATE OR REPLACE VIEW songs_by_artist AS
          (SELECT
             title,
             song_id,
             artist_id
           FROM songs, albums
           WHERE albums.artist_id = %s AND songs.album_id = albums.album_id
           GROUP BY title)""", artist_id

    @staticmethod
    def drop_view_songs_by_artist():
        return """DROP VIEW IF EXISTS songs_by_artist"""

    @staticmethod
    def create_view_songs_per_artists():
        return """CREATE OR REPLACE VIEW songs_per_artists AS
                      SELECT artist_id
                      FROM
                        (SELECT
                          artist_id,
                          count(*) AS songs_per_artist
                          FROM
                          (SELECT
                             title,
                             song_id,
                             albums.artist_id,
                             songs.album_id
                           FROM songs
                             JOIN albums ON songs.album_id = albums.album_id) AS T
                    GROUP BY artist_id) AS T2
                    WHERE songs_per_artist > 1"""

    @staticmethod
    def drop_view_songs_per_artists():
        return """DROP VIEW IF EXISTS songs_per_artists"""

    @staticmethod
    def get_n_random_artists(n):
        return """SELECT artist_id
                  FROM songs_per_artists
                  ORDER BY RAND()
                  LIMIT %s""", n

    @staticmethod
    def get_n_random_songs_by_artist(n):
        return """SELECT
                  title,
                  song_id
                  FROM songs_by_artist
                  ORDER BY RAND()
                  LIMIT %s""", n

    @staticmethod
    def get_artist_name_by_id(artist_id):
        return """SELECT name FROM artists WHERE artist_id = %s""", artist_id
