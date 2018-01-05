from flask import Flask, render_template, redirect, url_for, request, make_response, Response
import MySQLdb as mdb
from word_scraper import get5PopularWords
import random
import sys

app = Flask(__name__) # TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging

SCORE = 0
ANSWER_NUM = 0
NUM_QUESTIONS_PER_GAME = 5

@app.route('/translateGame')
def translate_game():
    global SCORE
    SCORE = 0
    global ANSWER_NUM
    ANSWER_NUM = 0

    con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic") #TODO: use assaf method when ready
    return create_game_page(con)


@app.route('/translateGame_')
def translate_game_mid():
    allow_access = request.cookies.get('allowAccess')
    if allow_access != 'true':
        return Response('You are not authorized to refresh in order to change question!', 401,
                        {'WWWAuthenticate': 'Basic realm="Login Required"'})
    global SCORE
    points = int(request.cookies.get('points'))
    SCORE += points
    global ANSWER_NUM
    ANSWER_NUM += 1
    global NUM_QUESTIONS_PER_GAME

    if ANSWER_NUM == NUM_QUESTIONS_PER_GAME:
        # TODO: call david's method for updating score with SCORE
        return redirect(url_for('hello_world')) # TODO: route to game choose page
    else:
        con = mdb.connect('localhost', 'root', 'Password!1', "mrmusic")
        return create_game_page(con)


def create_game_page(con):
    # Avoiding UnicodeDecodeError
    reload(sys)
    sys.setdefaultencoding('UTF8')

    translatedSongRow = calcTranslatedSongRow(con)
    translatedLyrics = translatedSongRow['hebrew_translation']
    rightAnswer = translatedSongRow['name']
    popularWords = get5PopularWords(translatedSongRow['lyrics'])  # TODO: do something if there is less then 5 words. should never happen
    wrongAnswers = calcAnswers(con, popularWords, translatedSongRow['song_id'],
                                translatedSongRow['name'], translatedSongRow['lyrics_language'])
    answers = random.sample(wrongAnswers + [rightAnswer], 4)
    functionCalls = []
    for i in range(len(answers)):
        if answers[i] == rightAnswer:
            functionCalls.append("onCorrectAnswer('button{}')".format(i + 1))
        else:
            functionCalls.append("onWrongAnswer('button{}')".format(i + 1))

    response = make_response(render_template('TranslateGame.html',
                                             question=translatedLyrics.decode('utf-8'),
                                             option_1=answers[0],
                                             option_2=answers[1],
                                             option_3=answers[2],
                                             option_4=answers[3],
                                             current_score=SCORE,
                                             funcCall1=functionCalls[0],
                                             funcCall2=functionCalls[1],
                                             funcCall3=functionCalls[2],
                                             funcCall4=functionCalls[3]))
    global ANSWER_NUM
    response.set_cookie('questionNum', str(ANSWER_NUM + 1))
    response.set_cookie('allowAccess', 'false')
    response.set_cookie('points', '0')  # setting points back to 0 to prevent cheating
    return response


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


def calcAnswers(con, popularWords, answerSongId, answerSongName, lyricsLang):

    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        query = createAnswersQuery(popularWords, answerSongId, answerSongName, lyricsLang)
        cur.execute(query)
        rows = cur.fetchall()

        res = []
        for row in rows:
            res.append(row['name'])
        return res


def createAnswersQuery(popularWords, answerSongId, answerSongName, lyricsLang):
    fillers = popularWords + [lyricsLang] + [answerSongId] + [answerSongName]
    #TODO: may improve the query with distint (befoe limit 3)
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
             'WHERE wordsCnt.song_id <> {6} AND songs.name <> \'{7}\'\n'
             'GROUP BY wordsCnt.song_id\n'
             'ORDER BY numWords DESC\n'
             'LIMIT 3').format(*fillers)
    return query





# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return "Imagine Assaf's Level Selection Page"

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run(debug=True)