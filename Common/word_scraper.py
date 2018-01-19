import operator
import string

#we use this module to parse lyrics

def has_only_letters(word):
    for ch in word:
        if ch not in string.letters:
            return False
    return True


def replace_punctuations(word):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in word if ch not in exclude)


def replace_slashn(word):
    # exclude = ['\n','\t','\r', '\u']
    exclude = string.whitespace
    return ''.join(ch for ch in word if ch not in exclude)


def get_dict_word_count(text):
    wordsToIgnore = ['a', 'although', 'an', 'are', 'as', 'because', 'before', 'el', 'for', 'her', 'i', 'if',
                     'in', 'is', 'it', 'la', 'me', 'mi', 'my', 'on', 'once', 'only', 'of', 'so', 'te', 'the',
                     'these', 'than', 'that', 'though', 'till', 'to', 'unless', 'when', 'whenever', 'where',
                     'wherever', 'while', 'with', 'you', 'was', '', ' ','were','be','he','she','im','your','and',
                     'has', 'his','hers', 'them', 'not', 'their', 'theirs','wanna','into', 'they','him','your',
                     'youre','by', 'thats','gonna', 'this','have', 'has', 'what', 'let', 'can', 'cant', 'even',
                     'more', 'few', 'non', 'none','which', 'we', 'our', 'at', 'and', 'dont']

    dict_of_words = dict()
    for word in text.split():  # changd from split(' ') to split()
        word = word.lower()
        word = replace_punctuations(word)
        word = replace_slashn(word)

        if (has_only_letters(word)) and word not in wordsToIgnore:
            if word not in dict_of_words:
                dict_of_words.update({word: 1})
            else:
                dict_of_words.update({word: dict_of_words[word] + 1})
    return dict_of_words

def sort_dict_by_value(dict_of_words):
    sorted_list = sorted(dict_of_words.items(), key=operator.itemgetter(1))
    return sorted_list


def get_5_popular_words(text):
    my_dict = get_dict_word_count(text)
    lst = sort_dict_by_value(my_dict)
    lst.reverse()
    result = []
    for i in range(0, 5):
        result.append(lst[i][0])
    return result
