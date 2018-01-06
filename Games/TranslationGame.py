from flask import Flask, render_template, redirect, url_for, request, make_response, Response
import MySQLdb as mdb
from word_scraper import get5PopularWords
import random
import sys
import GameManager

app = Flask(__name__)  # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging


NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager()


@app.route('/translateGame')
def translate_game():
    game_manager.start_new_game()

    con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")  # TODO: use assaf method when ready
    return create_game_page(con)


@app.route('/translateGame_')
def translate_game_mid():

    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME)

    if response is None:
        con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")
        return create_game_page(con)
    else:
        return response


def create_game_page(con):
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    translated_song_row = calc_translated_song_row(con)
    translated_lyrics = translated_song_row['hebrew_translation']
    right_answer = translated_song_row['name']
    # TODO: do something if there is less then 5 words. should never happen
    popular_words = get5PopularWords(translated_song_row['lyrics'])
    wrong_answers = calc_answers(con, popular_words, translated_song_row['song_id'],
                                 translated_song_row['name'], translated_song_row['lyrics_language'])
    answers = random.sample(wrong_answers + [right_answer], 4)

    response = make_response(render_template('TranslateGame.html',
                                             question=translated_lyrics.decode('utf-8'),
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=game_manager.score))

    response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
    return game_manager.update_cookies_for_new_question(response)


def calc_translated_song_row(con):

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute('SET character_set_results = \'utf8\', character_set_client = \'utf8\', '
                    'character_set_connection = \'utf8\','
                    'character_set_database = \'utf8\', character_set_server = \'utf8\'')
        query = ('SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.name\n'
                    'FROM lyrics JOIN songs ON lyrics.song_id = songs.sond_id\n'
                    'WHERE lyrics.hebrew_translation IS NOT NULL\n' 
                    'ORDER BY rand()\n'
                    'LIMIT 1')
        cur.execute(query)
        ans = cur.fetchone()
        return ans


def calc_answers(con, popular_words, answer_song_id, answer_song_name, lyrics_lang):

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        query = "SELECT DISTINCT songs.name, (count(*) - 1) AS numWords\n" \
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
                    ") AS wordsCnt ON wordsCnt.song_id = songs.sond_id\n" \
                "WHERE wordsCnt.song_id <> %s AND songs.name <> %s\n" \
                "GROUP BY wordsCnt.song_id\n" \
                "ORDER BY numWords DESC\n" \
                "LIMIT 3"

        # TODO: delete those print after testing
        print('translate query: ' + query)
        print('popular words: +'+popular_words[0] + ' +'+popular_words[1] + ' +'+popular_words[2] +
              ' +'+popular_words[3] + ' +'+popular_words[4] + '\nlyricsLang: ' + lyrics_lang + ' ,answerSongId: ' +
              str(answer_song_id) + ' ,answerSongName: ' + answer_song_name)

        cur.execute(query, ('+'+popular_words[0], lyrics_lang, '+'+popular_words[1], lyrics_lang, '+'+popular_words[2],
                            lyrics_lang, '+'+popular_words[3], lyrics_lang, '+'+popular_words[4], lyrics_lang,
                            answer_song_id, answer_song_name))
        rows = cur.fetchall()

        res = []
        for row in rows:
            res.append(row['name'])
        return res


# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return "Imagine Assaf's Level Selection Page"


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)