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
    wordsToIgnore = ['a', 'after', 'although', 'are', 'as', 'because', 'before', 'her', 'i', 'if', 'in', 'me', 'my',
                     'once', 'only', 'since', 'so', 'the', 'these', 'than', 'that', 'though', 'till', 'unless', 'until',
                     'when', 'whenever', 'where', 'wherever', 'while']
    #TODO maybe i will need to update this list
    dict_of_words = dict()
    for word in text.split(' '):
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

def get5PopularWords(text):
    my_dict = get_dict_word_count(text)
    lst = sort_dict_by_value(my_dict)
    lst.reverse()
    result = []
    for i in range(0, 5):
        result.append(lst[i][0])
    return result

if __name__ == '__main__':
    text = "Hello, I love you, won't you tell me your name? you you name"
    my_dict = get_dict_word_count(text)
    lst = sort_dict_by_value(my_dict)
    lst.reverse()
    print lst
    temp = get5PopularWords(text)
    print temp

