class QueryGenerator:

    def __init__(self):
        pass

    @staticmethod
    def sign_in_user():
        return """INSERT INTO users VALUES(%s,%s,%s)"""

    @staticmethod
    def get_user_data():
        return """SELECT * FROM users WHERE nickname = %s"""

    @staticmethod
    def get_email():
        return """SELECT * FROM users WHERE email = %s"""

    @staticmethod
    def update_password():
        return """UPDATE users SET hash_password=%s WHERE nickname=%s"""

    @staticmethod
    def create_score_update_query():
        return """INSERT INTO scores (nickname, date, game_id, score) VALUES (%s, %s, %s, %s)"""

    @staticmethod
    def setting_for_read_hebrew_from_db_query():
        return """SET character_set_results = 'utf8', character_set_client = 'utf8', 
                    character_set_connection = 'utf8',
                    character_set_database = 'utf8', character_set_server = 'utf8'"""

    @staticmethod
    def get_translated_song_question_query():
        return """SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.title
               FROM lyrics JOIN songs ON lyrics.song_id = songs.song_id
               WHERE lyrics.hebrew_translation IS NOT NULL AND CHAR_LENGTH(lyrics) > 200
               ORDER BY rand()
               LIMIT 1"""

    @staticmethod
    def get_duets_question_query():
        return """SELECT art1.artist_id, art1.artist_name, art2.artist_name 
                    FROM performed_by AS f_a1 JOIN performed_by AS f_a2 ON f_a1.song_id = f_a2.song_id
                          JOIN artists AS art1 ON f_a1.artist_id = art1.artist_id 
                          JOIN artists AS art2 ON art2.artist_id = f_a2.artist_id
                    WHERE f_a1.artist_id > f_a2.artist_id
                    GROUP BY f_a1.artist_id , f_a2.artist_id
                    ORDER BY rand()
                    LIMIT 1;"""

    @staticmethod
    def get_duets_answers_query():
        return """SELECT DISTINCT artist_name 
                    FROM artists
                    WHERE artist_name NOT LIKE %s AND artist_name NOT LIKE %s
                        AND artist_name NOT LIKE %s
                        AND artist_name NOT IN 
                                        (SELECT DISTINCT art.artist_name FROM 
                                            (SELECT song_id FROM performed_by WHERE artist_id = %s ) AS f_a1 
                                            JOIN performed_by AS f_a2 ON f_a1.song_id = f_a2.song_id 
                                            JOIN artists AS art ON f_a2.artist_id = art.artist_id
                                            WHERE f_a2.artist_id <> %s ) 
                                            ORDER BY rand()
                    LIMIT 3;"""

    @staticmethod
    def get_word_in_song_question_query():
        return """SELECT songs.song_id, songs.title, lyrics.lyrics
                   FROM lyrics JOIN songs ON lyrics.song_id = songs.song_id
                   WHERE songs.rank > 70
                   ORDER BY rand()
                   LIMIT 1"""

    @staticmethod
    def get_translated_song_answers_query():
        return """SELECT DISTINCT songs.title, (count(*) - 1) AS numWords
               FROM songs JOIN (
                   (SELECT song_id 
                   FROM lyrics
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)
                   UNION ALL
                   (SELECT song_id 
                   FROM lyrics 
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)
                   UNION ALL
                   (SELECT song_id 
                   FROM lyrics 
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)
                   UNION ALL
                   (SELECT song_id 
                   FROM lyrics
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)
                   UNION ALL
                   (SELECT song_id 
                   FROM lyrics
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)
                   UNION ALL 
                   (SELECT song_id FROM lyrics)
                   ) AS wordsCnt ON wordsCnt.song_id = songs.song_id
               WHERE wordsCnt.song_id <> %s AND songs.title <> %s
               GROUP BY wordsCnt.song_id
               ORDER BY numWords DESC
               LIMIT 3"""

    @staticmethod
    def get_top_ten_query():
        return """SELECT nickname, SUM(total_per_game.final_score_per_game) AS final_score
               FROM (SELECT total_per_game.nickname,total_per_game.game_id, ROUND(max_score + 10 *LOG2(total),2) AS final_score_per_game
                    FROM (SELECT nickname, game_id, SUM(score) AS total
                          FROM scores
                          GROUP BY nickname, game_id) AS total_per_game,
                          (SELECT nickname, game_id, MAX(score) AS max_score
                          FROM scores
                          GROUP BY nickname, game_id) AS max_per_game
                    WHERE total_per_game.nickname = max_per_game.nickname
                          AND total_per_game.game_id = max_per_game.game_id) AS total_per_game
               GROUP BY nickname
               ORDER BY final_score DESC
               LIMIT 10"""

    @staticmethod
    def get_top_ten_query_for_game():
        return """SELECT max_per_user.nickname AS nickname, ROUND(max_score + 10 *LOG2(total),2) AS final_score
                  FROM (SELECT nickname, SUM(score) AS total
                          FROM scores
                          WHERE game_id = %s
                          GROUP BY nickname) AS total_per_user,
                          (SELECT nickname, MAX(score) AS max_score
                          FROM scores
                          WHERE game_id = %s
                          GROUP BY nickname) AS max_per_user
                  WHERE total_per_user.nickname = max_per_user.nickname
                  GROUP BY nickname
                  ORDER BY final_score DESC"""

    @staticmethod
    def get_user_scores_for_game():
        return """SELECT ROUND(max_score + 10 *LOG2(total),2) AS final_score, total AS total_points
                  FROM (SELECT SUM(score) AS total
                          FROM scores
                          WHERE game_id = %s AND nickname = %s) AS total_for_user,
                          (SELECT MAX(score) AS max_score
                          FROM scores
                          WHERE game_id = %s AND nickname = %s) AS max_for_user"""

    @staticmethod
    def get_score():
        return """SELECT ROUND(SUM(total_per_game.final_score_per_game),2) AS final_score
                  FROM (SELECT total_per_game.game_id, (max_score + 10 *LOG2(total)) AS final_score_per_game
                        FROM (SELECT nickname, game_id, SUM(score) AS total
                              FROM scores
                              WHERE nickname = %s
                              GROUP BY game_id) AS total_per_game,
                              (SELECT nickname, game_id, MAX(score) AS max_score
                              FROM scores
                              WHERE nickname = %s
                              GROUP BY game_id) AS max_per_game
                        WHERE total_per_game.game_id = max_per_game.game_id) AS total_per_game"""

    @staticmethod
    def get_score_and_total_points():
        return """SELECT ROUND(SUM(total_per_game.final_score_per_game),2) AS final_score, SUM(total_points_per_game) AS total_points
                 FROM (SELECT total_per_game.game_id, (max_score + 10 *LOG2(total)) AS final_score_per_game, total AS total_points_per_game
                        FROM (SELECT nickname, game_id, SUM(score) AS total
                              FROM scores
                              WHERE nickname = %s
                              GROUP BY game_id) AS total_per_game,
                              (SELECT nickname, game_id, MAX(score) AS max_score
                              FROM scores
                              WHERE nickname = %s
                              GROUP BY game_id) AS max_per_game
                        WHERE total_per_game.game_id = max_per_game.game_id) AS total_per_game"""

    @staticmethod
    def get_release_order_question_query():
        return """SELECT albums.album_id, albums.release_month, albums.release_year, songs.title
               FROM albums JOIN songs ON albums.album_id = songs.album_id
               WHERE release_month IS NOT NULL AND rank >= 70
               ORDER BY rand()
               LIMIT 1"""

    @staticmethod
    def get_release_order_answers_query():
        return """SELECT monthDif, title
               FROM (
                    SELECT min(rowNum),  monthDif, title
                    FROM (
                        SELECT @n := @n + 1 rowNum, dateDist.*
                         FROM (SELECT @n:=0) initvars,
                              (SELECT IF(release_year = %s,
                                          %s - release_month,
                                          IF (release_year > %s,
                                              release_month + (12 - %s) + 12*(release_year-(%s+1)),
                                              -(%s + (12 - release_month) + 12*(%s-(release_year+1)) )) ) AS monthDif,
                                          songs.title
                                FROM albums JOIN songs ON albums.album_id = songs.album_id
                                WHERE release_month IS NOT NULL AND albums.album_id <> %s AND songs.title <> %s AND rank >= 70
                                GROUP BY songs.title
                                ORDER BY rand()) AS dateDist ) AS  dateDistWithNums
                    GROUP BY dateDistWithNums.monthDif 
                    HAVING dateDistWithNums.monthDif <> 0
                    ORDER BY abs(dateDistWithNums.monthDif)
                    LIMIT 3 ) AS closestReleased
               ORDER BY closestReleased.monthDif"""

    @staticmethod
    def get_n_random_artists():
        return """SELECT artist_id
                  FROM (SELECT artist_id
                        FROM
                          (SELECT
                             artist_id,
                             count(*) AS songs_per_artist
                           FROM
                             (SELECT
                                title,
                                songs.song_id,
                                artist_id
                              FROM songs
                                JOIN performed_by AS pb ON songs.song_id = pb.song_id
                              GROUP BY title) AS T
                           GROUP BY artist_id) AS T2
                        WHERE songs_per_artist > 1) AS songs_per_artist
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_n_random_songs_by_artist():
        return """SELECT
                    title,
                    song_id
                  FROM (SELECT
                          title,
                          songs.song_id,
                          artist_id
                        FROM songs, performed_by
                        WHERE performed_by.artist_id = %s AND songs.song_id = performed_by.song_id) AS songs_by_artist
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_artist_name_by_id():
        return """SELECT artist_name FROM artists WHERE artist_id = %s"""

    @staticmethod
    def get_n_random_countries():
        return """SELECT country_name
                  FROM (SELECT
                          country_name,
                          artists_per_country
                        FROM
                          (SELECT
                             artists.country_name,
                             COUNT(*) AS artists_per_country
                           FROM artists,
                             (SELECT DISTINCT country_name
                              FROM artists
                              WHERE country_name != '') AS countries
                           WHERE artists.country_name = countries.country_name
                           GROUP BY artists.country_name) AS T
                        WHERE artists_per_country > 1) AS artists_per_country
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_n_artists_from_country():
        return """SELECT artist_id
                  FROM artists
                  WHERE country_name = %s
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_n_random_artists_from_possible_artists():
        return """SELECT artist_id
                  FROM (SELECT artist_id
                          FROM (SELECT
                                  artist_id,
                                  COUNT(*) AS num_of_albums
                                FROM albums
                                WHERE albums_cover IS NOT NULL AND albums_cover NOT LIKE '%%nocover%%'
                                GROUP BY artist_id) AS albums_per_artist
                  WHERE num_of_albums > 1) AS possible_artists
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_n_album_covers_from_artist():
        return """SELECT albums_cover
                  FROM albums
                  WHERE albums_cover IS NOT NULL AND albums_cover NOT LIKE '%%nocover%%' AND artist_id = %s
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_four_ranked_songs_in_country():
        return """SELECT
                    top_for_country.song_name  AS highest_rank,
                    top_for_country2.song_name AS alternative1,
                    top_for_country3.song_name AS alternative2,
                    top_for_country4.song_name AS alternative3
                  FROM (SELECT
                          songs.title                   AS song_name,
                          popular_songs_by_country.rank AS song_rank
                        FROM songs, popular_songs_by_country
                        WHERE songs.song_id = popular_songs_by_country.song_id
                              AND popular_songs_by_country.country_name = %s) AS top_for_country,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country2,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country3,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country4
                  WHERE top_for_country.song_rank < top_for_country2.song_rank
                        AND top_for_country2.song_rank < top_for_country3.song_rank
                        AND top_for_country3.song_rank < top_for_country4.song_rank
                        AND top_for_country2.song_rank - top_for_country.song_rank <= 5
                        AND top_for_country3.song_rank - top_for_country2.song_rank >= 10
                        AND top_for_country3.song_rank - top_for_country2.song_rank <= 30
                        AND top_for_country4.song_rank - top_for_country2.song_rank >= 50
                  ORDER BY RAND()
                  LIMIT 1"""

    @staticmethod
    def get_song_ranking_in_four_countries():
        return """SELECT
                    top_for_country1.song_name AS song_name,
                    top_for_country1.song_rank AS rank1,
                    top_for_country2.song_rank AS rank2,
                    top_for_country3.song_rank AS rank3,
                    top_for_country4.song_rank AS rank4
                  FROM (SELECT
                          songs.title                   AS song_name,
                          popular_songs_by_country.rank AS song_rank
                        FROM songs, popular_songs_by_country
                        WHERE songs.song_id = popular_songs_by_country.song_id
                              AND popular_songs_by_country.country_name = %s) AS top_for_country1,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country2,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country3,
                    (SELECT
                       songs.title                   AS song_name,
                       popular_songs_by_country.rank AS song_rank
                     FROM songs, popular_songs_by_country
                     WHERE songs.song_id = popular_songs_by_country.song_id
                           AND popular_songs_by_country.country_name = %s) AS top_for_country4
                  WHERE top_for_country1.song_name = top_for_country2.song_name
                        AND top_for_country2.song_name = top_for_country3.song_name
                        AND top_for_country3.song_name = top_for_country4.song_name
                        AND top_for_country1.song_rank != top_for_country2.song_rank
                        AND top_for_country1.song_rank != top_for_country3.song_rank
                        AND top_for_country1.song_rank != top_for_country4.song_rank
                        AND top_for_country2.song_rank != top_for_country3.song_rank
                        AND top_for_country2.song_rank != top_for_country4.song_rank
                        AND top_for_country3.song_rank != top_for_country4.song_rank
                  ORDER BY RAND()
                  LIMIT 1"""

    @staticmethod
    def get_songs_lyrics_contain():
        return """SELECT DISTINCT songs.title
                  FROM songs
                    INNER JOIN (
                                 SELECT
                                   song_id,
                                   lyrics
                                 FROM lyrics
                                 WHERE lyrics_language = 'en'
                                       AND MATCH(lyrics) AGAINST(%s IN NATURAL LANGUAGE MODE)) lycs
                      ON songs.song_id = lycs.song_id
                  WHERE songs.title NOT LIKE %s
                  ORDER BY rand()
                  LIMIT 3"""

    @staticmethod
    def get_songs_lyrics_not_contain():
        return """SELECT songs.title
                  FROM songs
                    INNER JOIN (
                                 SELECT DISTINCT songs.title AS songname
                                 FROM songs
                                   INNER JOIN (SELECT
                                                 song_id,
                                                 lyrics
                                               FROM lyrics
                                               WHERE lyrics_language = 'en'
                                                     AND NOT Match(lyrics) AGAINST(%s IN NATURAL LANGUAGE MODE)) lycs
                                     ON songs.song_id = lycs.song_id
                                 WHERE songs.title NOT LIKE %s) temp ON temp.songname = songs.title
                  WHERE songs.title = %s"""
