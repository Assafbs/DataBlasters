import random

import MySQLdb as mdb
from flask import Flask, render_template

from word_scraper import get5PopularWords

app = Flask(__name__)


@app.route('/translateLevel')
def calc_question_and_ans():
    score = 0
    con = mdb.connect('localhost', 'root', 'Password!1', "my_schema")
    # TODO: loop of number of questions i want to ask the user (10?) - after 1 question will work
    translated_song_row = calc_translated_song_row(con)
    translated_lyrics = translated_song_row['hebrew_translation']
    right_answer = translated_song_row['name']
    popular_words = get5PopularWords(translated_song_row['lyrics'])  # TODO: do somethig if ther is less then 5 words. should never happen
    wrong_answers = calc_answers(con, popular_words, translated_song_row['song_id'], translated_song_row['lyrics_language'])
    answers = random.sample(wrong_answers + [right_answer], 4)

    # TODO: need to define onClick for each button which will mark in red, or mark in green and add points to score
    #       TODO: maybe on click will route to this page again (and in the last iteration to levels page (maybe after presenting the score))
    # TODO: understand how to change the ui params in end of iteration - after 1 question will work
    return render_template('translateLevel.html',
                           question=translated_lyrics,
                           option_1=answers[0],
                           option_2=answers[1],
                           option_3=answers[2],
                           option_4=answers[3],
                           current_score=score)


def calc_translated_song_row(con):
    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        query = ('SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.name\n'
                 'FROM lyrics JOIN songs ON lyrics.song_id = songs.sond_id\n'
                 'WHERE lyrics.hebrew_translation IS NOT NULL\n'
                 'ORDER BY rand()\n'
                 'LIMIT 1')
        cur.execute(query)
        ans = cur.fetchone()
        return ans


def calc_answers(con, popular_words, answer_song_id, lyrics_lang):
    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        query = create_answers_query(popular_words, answer_song_id, lyrics_lang)
        cur.execute(query)
        rows = cur.fetchall()

        res = []
        for row in rows:
            res.append(row['name'])
        return res


def create_answers_query(popular_words, answer_song_id, lyrics_lang):
    fillers = popular_words + [lyrics_lang] + [answer_song_id]
    query = ('SELECT songs.name, (count(*) - 1) AS numWords\n'
             'FROM songs JOIN (\n'
             '(SELECT song_id \n'
             'FROM lyrics \n'
             'WHERE MATCH(lyrics) AGAINST(\'+{0}\' IN BOOLEAN MODE) AND lyrics_language = \'{5}\')\n'
             'UNION ALL\n'
             '(SELECT song_id \n'
             'FROM lyrics \n'
             'WHERE MATCH(lyrics) AGAINST(\'+{1}\' IN BOOLEAN MODE) AND lyrics_language = \'{5}\')\n'
             'UNION ALL\n'
             '(SELECT song_id \n'
             'FROM lyrics\n'
             'WHERE MATCH(lyrics) AGAINST(\'+{2}\' IN BOOLEAN MODE) AND lyrics_language = \'{5}\')\n'
             'UNION ALL\n'
             '(SELECT song_id\n'
             'FROM lyrics \n'
             'WHERE MATCH(lyrics) AGAINST(\'+{3}\' IN BOOLEAN MODE) AND lyrics_language = \'{5}\')\n'
             'UNION ALL'
             '(SELECT song_id\n'
             'FROM lyrics \n'
             'WHERE MATCH(lyrics) AGAINST(\'+{4}\' IN BOOLEAN MODE) AND lyrics_language = \'{5}\')\n'
             'UNION ALL(SELECT song_id \n'
             'FROM lyrics) \n'
             ') AS wordsCnt ON wordsCnt.song_id = songs.song_id\n'
             'WHERE wordsCnt.song_id <> {6}\n'
             'GROUP BY wordsCnt.song_id\n'
             'ORDER BY numWords DESC\n'
             'LIMIT 3').format(*fillers)
    return query


# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return 'Hello World!'


# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run()
