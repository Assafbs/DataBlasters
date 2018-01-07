import time


class QueryGenerator:

    def __init__(self):
        pass

    @staticmethod
    def create_score_update_query(nickname, game_id, score):
        return "INSERT INTO scores (nickname, date, game_id, score) VALUES (%s, %s, %s, %s)", (nickname, time.strftime('%Y-%m-%d %H:%M:%S'), game_id, score)

    @staticmethod
    def get_translated_song_query():
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
