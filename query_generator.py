class QueryGenerator:

    def __init__(self):
        pass

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
        return """SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.title\n
               FROM lyrics JOIN songs ON lyrics.song_id = songs.song_id\n
               WHERE lyrics.hebrew_translation IS NOT NULL AND CHAR_LENGTH(lyrics) > 200\n
               ORDER BY rand()\n
               LIMIT 1"""

    @staticmethod
    def get_translated_song_answers_query():
        return """SELECT DISTINCT songs.title, (count(*) - 1) AS numWords\n
               FROM songs JOIN (\n
                   (SELECT song_id \n
                   FROM lyrics\n
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n
                   UNION ALL\n
                   (SELECT song_id \n
                   FROM lyrics \n
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n
                   UNION ALL\n
                   (SELECT song_id \n
                   FROM lyrics \n
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n
                   UNION ALL\n
                   (SELECT song_id \n
                   FROM lyrics\n
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n
                   UNION ALL\n
                   (SELECT song_id \n
                   FROM lyrics\n
                   WHERE MATCH(lyrics) AGAINST(%s IN BOOLEAN MODE) AND lyrics_language = %s)\n
                   UNION ALL \n
                   (SELECT song_id FROM lyrics)\n
                   ) AS wordsCnt ON wordsCnt.song_id = songs.song_id\n
               WHERE wordsCnt.song_id <> %s AND songs.title <> %s\n
               GROUP BY wordsCnt.song_id\n
               ORDER BY numWords DESC\n
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
    def get_release_order_question_query():
        return """SELECT albums.album_id, albums.release_month, albums.release_year, songs.title\n
               FROM albums JOIN songs ON albums.album_id = songs.album_id\n
               WHERE release_month IS NOT NULL AND rank > 70\n
               ORDER BY rand()\n
               LIMIT 1"""

    @staticmethod
    def get_release_order_answers_query():
        return """SELECT monthDif, title\n
               FROM (\n
                    SELECT min(rowNum),  monthDif, title\n
                    FROM (\n
                        SELECT @n := @n + 1 rowNum, dateDist.*\n
                         FROM (SELECT @n:=0) initvars,\n
                              (SELECT IF(release_year = %s,\n
                                          %s - release_month,\n
                                          IF (release_year > %s,\n
                                              release_month + (12 - %s) + 12*(release_year-(%s+1)),\n
                                              -(%s + (12 - release_month) + 12*(%s-(release_year+1)) )) ) AS monthDif,\n
                                          songs.title\n
                                FROM albums JOIN songs ON albums.album_id = songs.album_id\n
                                WHERE release_month IS NOT NULL AND albums.album_id <> %s AND rank > 70\n
                                ORDER BY rand()) AS dateDist ) AS  dateDistWithNums\n
                    GROUP BY dateDistWithNums.monthDif \n
                    HAVING dateDistWithNums.monthDif <> 0\n
                    ORDER BY abs(dateDistWithNums.monthDif)\n
                    LIMIT 3 ) AS closestReleased\n
               ORDER BY closestReleased.monthDif"""

    @staticmethod
    def create_view_songs_by_artist():
        return """CREATE OR REPLACE VIEW songs_by_artist AS
          (SELECT
            title,
            songs.song_id,
            artist_id
          FROM songs, performed_by
          WHERE performed_by.artist_id = %s AND songs.song_id = performed_by.song_id)"""

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
                              songs.song_id,
                              artist_id
                            FROM songs
                              JOIN performed_by AS pb ON songs.song_id = pb.song_id
                              GROUP BY title) AS T
                         GROUP BY artist_id) AS T2
                      WHERE songs_per_artist > 1"""

    @staticmethod
    def drop_view_songs_per_artists():
        return """DROP VIEW IF EXISTS songs_per_artists"""

    @staticmethod
    def get_n_random_artists():
        return """SELECT artist_id
                  FROM songs_per_artists
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_n_random_songs_by_artist():
        return """SELECT
                  title,
                  song_id
                  FROM songs_by_artist
                  ORDER BY RAND()
                  LIMIT %s"""

    @staticmethod
    def get_artist_name_by_id():
        return """SELECT name FROM artists WHERE artist_id = %s"""

    @staticmethod
    def create_view_artists_per_country():
        return """CREATE OR REPLACE VIEW artists_per_country AS
                    SELECT
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
                    WHERE artists_per_country > 1"""

    @staticmethod
    def drop_view_artists_per_country():
        return """DROP VIEW IF EXISTS songs_per_artists"""

    @staticmethod
    def get_n_random_countries():
        return """SELECT country_name
                  FROM artists_per_country
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
    def create_view_possible_artists():
        return """CREATE OR REPLACE VIEW possible_artists AS
                    SELECT artist_id
                    FROM
                      (SELECT
                         artist_id,
                         COUNT(*) AS num_of_albums
                       FROM albums
                       WHERE albums_cover IS NOT NULL AND albums_cover NOT LIKE '%%nocover%%'
                       GROUP BY artist_id) AS albums_per_artist
                    WHERE num_of_albums > 1"""

    @staticmethod
    def drop_view_possible_views():
        return """DROP VIEW IF EXISTS possible_artists"""

    @staticmethod
    def get_n_random_artists_from_possible_artists():
        return """SELECT artist_id
                      FROM possible_artists
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
        return """SELECT top_for_country.song_name AS highest_rank, top_for_country2.song_name AS alternative1,
                         top_for_country3.song_name AS alternative2,  top_for_country4.song_name AS alternative3
                  FROM  (SELECT songs.name AS song_name, popular_songs_by_country.rank AS song_rank
	                    FROM songs, popular_songs_by_country 
	                    WHERE songs.song_id = popular_songs_by_country.song_id
	                    AND popular_songs_by_country.country_name = %s) AS top_for_country,
                        (SELECT songs.name AS song_name, popular_songs_by_country.rank AS song_rank
	                    FROM songs, popular_songs_by_country 
	                    WHERE songs.song_id = popular_songs_by_country.song_id
	                    AND popular_songs_by_country.country_name = %s) AS top_for_country2,
                        (SELECT songs.name AS song_name, popular_songs_by_country.rank AS song_rank
	                    FROM songs, popular_songs_by_country 
	                    WHERE songs.song_id = popular_songs_by_country.song_id
	                    AND popular_songs_by_country.country_name = %s) AS top_for_country3,
                        (SELECT songs.name AS song_name, popular_songs_by_country.rank AS song_rank
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
        return """SELECT top_for_country1.song_name AS song_name,
                         top_for_country1.song_rank AS rank1,
                         top_for_country2.song_rank AS rank2,
                         top_for_country3.song_rank AS rank3,
                         top_for_country4.song_rank AS rank4
                  FROM  (SELECT songs.name AS song_name, popular_songs.rank AS song_rank
	                     FROM songs, popular_songs 
	                     WHERE songs.song_id = popular_songs.song_id
	                     AND popular_songs.country_name = %s) AS top_for_country1,
                         (SELECT songs.name AS song_name, popular_songs.rank AS song_rank
	                     FROM songs, popular_songs 
	                     WHERE songs.song_id = popular_songs.song_id
                     	 AND popular_songs.country_name = %s) AS top_for_country2,
                         (SELECT songs.name AS song_name, popular_songs.rank AS song_rank
	                     FROM songs, popular_songs 
	                     WHERE songs.song_id = popular_songs.song_id
	                     AND popular_songs.country_name = %s) AS top_for_country3,
                         (SELECT songs.name AS song_name, popular_songs.rank AS song_rank
	                     FROM songs, popular_songs 
	                     WHERE songs.song_id = popular_songs.song_id
	                     AND popular_songs.country_name = %s) AS top_for_country4
                  WHERE top_for_country1.song_name = top_for_country2.song_name
		                AND top_for_country2.song_name = top_for_country3.song_name
                        AND top_for_country3.song_name = top_for_country4.song_name
                        AND top_for_country1.song_rank != top_for_country2.song_rank 
                        AND top_for_country1.song_rank != top_for_country3.song_rank 
                        AND top_for_country1.song_rank != top_for_country4.song_rank
                        AND top_for_country2.song_rank != top_for_country3.song_rank 
                        AND top_for_country2.song_rank != top_for_country4.song_rank 
                        AND top_for_country3.song_rank != top_for_country4.song_rank
                  ORDER BY RAND()"""

    @staticmethod
    def get_songs_lyrics_contain():
        return """SELECT DISTINCT songs.name
        FROM songs INNER JOIN(
                    SELECT song_id,lyrics
                    FROM dbmysql09.lyrics
					WHERE lyrics_language='en'
                    AND MATCH(lyrics) AGAINST('%s' in natural language mode))lycs 
				ON songs.song_id=lycs.song_id
		WHERE songs.name NOT LIKE %s
		ORDER BY rand()
        LIMIT 3"""

    @staticmethod
    def get_songs_lyrics_not_contain():
        return """SELECT songs.name
        FROM dbmysql09.songs INNER JOIN(
	        SELECT DISTINCT songs.name as songname
	        FROM dbmysql09.songs INNER JOIN(SELECT song_id,lyrics
									    FROM dbmysql09.lyrics
									    WHERE lyrics_language='en'
									    AND NOT Match(lyrics) AGAINST(%s in natural language mode))lycs 
						        ON songs.song_id=lycs.song_id
	        WHERE songs.name NOT LIKE %s)temp ON temp.songname=songs.name
        WHERE songs.name=%s"""