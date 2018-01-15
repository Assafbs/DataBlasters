import operator
import string
import re

def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


def has_letters(word):
    if not re.search('[a-zA-Z]', word):
        print word


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
                     'wherever', 'while', 'with', 'you','use','lyrics','commercial','',' ']
    #TODO can remove use,lyrics,commercial from list when working with clean lyrics
    dict_of_words = dict()
    for word in text.split(): #changd from split(' ') to split()
        word = word.lower()
        word = replace_punctuations(word)
        word = replace_slashn(word)

        if (has_only_letters(word)) and word not in wordsToIgnore:
            if word not in dict_of_words:
                dict_of_words.update({word: 1})
            else:
                dict_of_words.update({word: dict_of_words[word] + 1})
    return dict_of_words


def print_dict(dictionary):
    for key in dictionary.keys():
        if len(dictionary[key]) > 3:
            print "key: " + key
            for word in dictionary[key]:
                print word
            print "\n"


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

if __name__ == '__main__':
    text = 'Old friends, old friends Sat on their park bench like bookends A newspaper blown through the grass Falls on the round toes Of the high shoes of the old friends'

    my_dict = get_dict_word_count(text)
    lst = sort_dict_by_value(my_dict)
    lst.reverse()
    print lst
    temp = get_5_popular_words(text)
    print temp

