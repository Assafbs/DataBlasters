from flask import Flask, render_template, redirect, url_for, request, make_response,session
app = Flask(__name__)


@app.route('/translateLevel')
def calcQuestionAndAns():
    # score = 0
    # TODO: loop of number of questions i want to ask the user (10?) - after 1 question will work
    # row = calcQuestionRow()
    # question = row[3]
    # rightAns = row[4]
    # take row[1] (the lyrics) and calc with david code the 5 popular words
    # call calcAns with the 5 popular words and row[0] (the song id) and row[2] (the lang)
    # wrongAnswers = the return value from above line
    # TODO: need to mix the answers so the right ans will apear in different place each time
    # TODO: need to define onClick for each bottun which will mark in red, or mark in green and add points to score
    #       TODO: maybe on click will route to this page again (and in the last iteration to levels page (maybe after presenting the score))
    # TODO: understant how to change the ui params in end of iteration - after 1 question will work
    return render_template('translateLevel.html', question='chooseLetter', option_1='A', option_2='B', option_3='C', option_4='D')


def calcQuestionRow():
    # create sql connection
    query = ('SELECT lyrics.song_id, lyrics.lyrics, lyrics.lyrics_language, lyrics.hebrew_translation, songs.name'
                'FROM lyrics JOIN songs ON lyrics.song_id = songs.sond_id'
                'WHERE lyrics.hebrew_translation IS NOT NULL'
                'ORDER BY rand()'
                'LIMIT 1')
    # execute query
    # return the ans row

# TODO: need to find the 5 popular words before calling calcAns


def calcAnswers():
    # create sql connection
    query = ('')
    # cursor.execute("UPDATE Writers SET Name = %s WHERE Id = %s", ("Leo Tolstoy", "1"))
    # execute query
    # return list of the answers





# TODO: delete the / route, this is just for debugging
@app.route('/')
def hello_world():
    return 'Hello World!'

# TODO: delete this, it should be only in 1 place (main page or something). this is just for debugging
if __name__ == '__main__':
    app.run()