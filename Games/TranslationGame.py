from flask import Flask, render_template, redirect, url_for, request, make_response,session
import MySQLdb as mdb
from word_scraper import get5PopularWords
import random

app = Flask(__name__) # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging


@app.route('/translateGame')
def calcQuestionAndAns():
    score = 0
    con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")
    # TODO: loop of number of questions i want to ask the user (10?) - after 1 question will work
    translatedSongRow = calcTranslatedSongRow(con)
    translatedLyrics = translatedSongRow['hebrew_translation']
    rightAnswer = translatedSongRow['name']
    popularWords = get5PopularWords(translatedSongRow['lyrics']) #TODO: do somethig if ther is less then 5 words. should never happen
    wrongAnswers = calcAnswers(con, popularWords, translatedSongRow['song_id'], translatedSongRow['lyrics_language'])
    answers = random.sample(wrongAnswers + [rightAnswer], 4)
    functionCalls = []
    for i in range(len(answers)):
        if answers[i] == rightAnswer:
            functionCalls.append("onCorrectAnswer('button{}')".format(i+1))
        else:
            functionCalls.append("onWrongAnswer('button{}')".format(i+1))



    # TODO: need to define onClick for each bottun which will mark in red, or mark in green and add points to score
    #       TODO: maybe on click will route to this page again (and in the last iteration to levels page (maybe after presenting the score))
    # TODO: understant how to change the ui params in end of iteration - after 1 question will work
    return render_template('TranslateGame.html',
                           question=translatedLyrics.decode('utf-8'),
                           option_1=answers[0],
                           method1=onRightAnswer,
                           option_2=answers[1],
                           option_3=answers[2],
                           option_4=answers[3],
                           current_score=score,
                           funcCall1=functionCalls[0],
                           funcCall2=functionCalls[1],
                           funcCall3=functionCalls[2],
                           funcCall4=functionCalls[3])


def calcTranslatedSongRow(con):

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute('SET character_set_results = \'utf8\', character_set_client = \'utf8\', '
                    'character_set_connection = \'utf8\','
                    'character_set_database = \'utf8\', character_set_server = \'utf8\'') # TODO: delete
        query = ('SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.name\n'
                    'FROM lyrics JOIN songs ON lyrics.song_id = songs.sond_id\n'
                    'WHERE lyrics.hebrew_translation IS NOT NULL\n' 
                    'ORDER BY rand()\n'
                    'LIMIT 1')
        cur.execute(query)
        ans = cur.fetchone()
        return ans


def calcAnswers(con, popularWords, answerSongId, lyricsLang):

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        query = createAnswersQuery(popularWords, answerSongId, lyricsLang)
        cur.execute(query)
        rows = cur.fetchall()

        res = []
        for row in rows:
            res.append(row['name'])
        return res


def createAnswersQuery(popularWords, answerSongId, lyricsLang):
    fillers = popularWords + [lyricsLang] + [answerSongId] #TODO: may improve the query with distint (befoe limit 3)
    query = ('SELECT DISTINCT songs.name, (count(*) - 1) AS numWords\n'
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
                 ') AS wordsCnt ON wordsCnt.song_id = songs.sond_id\n'
             'WHERE wordsCnt.song_id <> {6}\n'
             'GROUP BY wordsCnt.song_id\n'
             'ORDER BY numWords DESC\n'
             'LIMIT 3').format(*fillers)
    return query


def onRightAnswer(): #TODO: this method can't be called directly from the html. need JS in the middle
    print('onRightAnswer!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return "Imagine Assaf's Level Selection Page"

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)