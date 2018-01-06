class QueryGenerator:

    def __init__(self):
        pass

    def get_translated_song_query(self):
        return "SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.name\n" \
        "FROM lyrics JOIN songs ON lyrics.song_id = songs.sond_id\n" \
        "WHERE lyrics.hebrew_translation IS NOT NULL\n" \
        "ORDER BY rand()\n" \
        "LIMIT 1"

    def get_translated_song_answers_qurty(self):
        return "SELECT DISTINCT songs.name, (count(*) - 1) AS numWords\n" \
        "FROM songs JOIN (\n" \
        "(SELECT song_id \n"\
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
        ") AS wordsCnt ON wordsCnt.song_id = songs.sond_id\n" \
        "WHERE wordsCnt.song_id <> %s AND songs.name <> %s\n" \
        "GROUP BY wordsCnt.song_id\n" \
        "ORDER BY numWords DESC\n" \
        "LIMIT 3"