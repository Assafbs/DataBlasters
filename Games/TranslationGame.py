from flask import Flask, render_template, redirect, url_for, request, make_response,session
import MySQLdb as mdb
from word_scraper import get5PopularWords

app = Flask(__name__)


@app.route('/translateLevel')
def calcQuestionAndAns():
    score = 0
    con = mdb.connect('localhost', 'root', 'Password!1', "my_schema")
    # TODO: loop of number of questions i want to ask the user (10?) - after 1 question will work
    translatedSongRow = calcTranslatedSongRow(con)
    translatedLyrics = translatedSongRow['hebrew_translation']
    rightAns = translatedSongRow['name']
    popularWords = get5PopularWords(translatedSongRow['lyrics']) #TODO: do somethig if ther is less then 5 words. should never happen
    wrongAnswers = calcAnswers(con, popularWords, translatedSongRow['song_id'], translatedSongRow['lyrics_language'])


    # TODO: need to mix the answers so the right ans will apear in different place each time
    # TODO: need to define onClick for each bottun which will mark in red, or mark in green and add points to score
    #       TODO: maybe on click will route to this page again (and in the last iteration to levels page (maybe after presenting the score))
    # TODO: understant how to change the ui params in end of iteration - after 1 question will work
    return render_template('translateLevel.html',
                           question=translatedLyrics,
                           option_1=rightAns,
                           option_2=wrongAnswers[0],
                           option_3=wrongAnswers[1],
                           option_4=wrongAnswers[2],
                           current_score=score)


def calcTranslatedSongRow(con):

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


# TODO: need to find the 5 popular words before calling calcAns


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
    fillers = popularWords + [lyricsLang] + [answerSongId]
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
                 ') AS wordsCnt ON wordsCnt.song_id = songs.sond_id\n'
             'WHERE wordsCnt.song_id <> {6}\n'
             'GROUP BY wordsCnt.song_id\n'
             'ORDER BY numWords DESC\n'
             'LIMIT 3').format(*fillers)
    #TODO: the format isn't working + popular words return words like: in , i, the etc.
    return query



# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return 'Hello World!'

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run()