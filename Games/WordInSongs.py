from word_scraper import get_dict_word_count
from db_connector import DbConnector
from flask import Blueprint, render_template, request, make_response
from query_generator import QueryGenerator
import pickle
import GameManager
import random
from word_scraper import get_5_popular_words

GAME_ID = 4
NUM_QUESTIONS_PER_GAME = 5
game_manager = GameManager.GameManager(GAME_ID)
filename='../Games/frqWordCountDict.pickle'

word_in_songs=Blueprint('word_in_songs', __name__, template_folder='templates')

@word_in_songs.route('/word_in_songs')
def word_in_songs_game_start():
    game_manager.start_new_game()
    return create_game_page()

word_in_songs_ = Blueprint('word_in_songs_', __name__, template_folder='templates')
@word_in_songs_.route('/word_in_songs_')
def word_in_songs_game_mid():

    allow_access = request.cookies.get('allowAccess')
    points = int(request.cookies.get('points'))
    response = game_manager.calc_mid_game(allow_access, points, NUM_QUESTIONS_PER_GAME, request)

    if response is None:
        return create_game_page()
    else:
        return response

def create_game_page():
    # if game_manager.answer_num % 2 == 1:
    #     return create_words_in_song_game_page()
    # else:
        return create_3_songs_game_page()

def create_3_songs_game_page():
    # Avoiding UnicodeDecodeError
    #reload(sys)
    #sys.setdefaultencoding('UTF8')

    with open(filename, 'rb') as fwcd:
        word_dict = pickle.load(fwcd)
    correct_answer=random.choice(word_dict.keys())
    connector = DbConnector()
    data = connector.get_all_results_for_query(QueryGenerator.get_songs_lyrics_contain(),(correct_answer,correct_answer))
    songs=[tup[0] for tup in data]
    wrong_answers= get_wrong_answers(connector,correct_answer,songs,word_dict) #TODO, returns 3 wrong answers
    connector.close()
    answers=random.sample(wrong_answers+[correct_answer],4)
    try:
        response = make_response(render_template('WordInSongs.html',
                                                 songName1=songs[0],
                                                 songName2=songs[1],
                                                 songName3=songs[2],
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=game_manager.score,
                                                 current_score=game_manager.score))

        response.set_cookie('correctAnswerNum', str(answers.index(correct_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_game_page()


def get_wrong_answers(connector,correct_answer,songs,word_dict):

    #use query on three words.
    # if there is one song that contains non of the words-ok.
    #else keep randomizign -- think of a better way to do that..
    res = []
    while (len(res)<3):
        answer=random.choice(word_dict.keys())
        while(answer==correct_answer):
            answer = random.choice(word_dict.keys())
        for song in songs: #every answer should have at least one song it does not appear in
            data=connector.get_all_results_for_query(QueryGenerator.get_songs_lyrics_not_contain(),
                                                     (answer,answer,song)) #might need to add '' to args
            if len(data)>0: #if we get back the name of the song, answer is not in it
                res.append(answer)
                break
            else:
                continue
    return res


def create_words_in_song_game_page():

    connector = DbConnector()
    song_row = connector.get_one_result_for_query(QueryGenerator.get_word_in_song_question_query())

    lyrics = song_row[2]
    popular_words = get_5_popular_words(lyrics)
    right_answer = popular_words[0];
    wrong_answers = popular_words[1:4]

    connector.close()
    answers = random.sample(wrong_answers + [right_answer], 4)

    try:
        response = make_response(render_template('WordInSongGame.html',
                                                 question=song_row[1],
                                                 option_1=answers[0],
                                                 option_2=answers[1],
                                                 option_3=answers[2],
                                                 option_4=answers[3],
                                                 game=game_manager.answer_num + 1,
                                                 score=game_manager.score,
                                                 current_score=game_manager.score))

        response.set_cookie('correctAnswerNum', str(answers.index(right_answer) + 1))
        return game_manager.update_cookies_for_new_question(response)
    except Exception as e:
        print "Error occurred with response"
        print e.message
        create_game_page()

############################

frq_word_dict=dict()
ign_words=['he', 'she', 'her', 'has', 'his', 'hers', 'them', 'not', 'their', 'theirs'
           'they','him','shes','hes','your','youre','be','by','thats','in'
           'into','was','were','wanna','gonna','this','im','have','has'
           'what','let','can','cant','even','more','few','non','none','wanna'
           'use','only','commercial','','lyrics','which','we','our','at','and','dont']
#TODO on the real db there is not line about commercial use so cand delete use,commercial and lyrics from list

def build_frq_word_dict():
    global frq_word_dict
    query="SELECT lyrics FROM lyrics WHERE lyrics_language=%s"
    con=DbConnector()
    data=con.get_all_results_for_query(query,('en',))
    for lyc in data:
        words_count=get_dict_word_count(lyc[0])
        for word in words_count:
            if word not in ign_words:
                if word not in frq_word_dict:
                    frq_word_dict.update({word:1})
                else:
                    frq_word_dict.update({word:frq_word_dict[word]+1})
    del_lst=[]
    for key in frq_word_dict:
        if frq_word_dict[key]<20:
            del_lst.append(key)
    for key in del_lst:
        frq_word_dict.pop(key,None)
    return

# build_frq_word_dict()
# newfile='frqWordCountDict.pickle'
# with open(newfile,'wb') as fwcd:
#    pickle.dump(frq_word_dict,fwcd)
#
# with open(newfile,'rb') as fwcd:
#    dictionary=pickle.load(fwcd)
# print dictionary==frq_word_dict

