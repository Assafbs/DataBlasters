import string
import re
from difflib import SequenceMatcher

class RedundancyHandler:

    def __init__(self):
        pass

    @staticmethod
    def areSimilar(word1, word2, minimal_similarity):
        # Make them lower case.
        word1 = word1.lower()
        word2 = word2.lower()
        # Remove punctuation.
        word1 = word1.translate(None, string.punctuation)
        word2 = word2.translate(None, string.punctuation)
        # Remove redundant spaces.
        word1 = re.sub(' +', ' ', word1)
        word2 = re.sub(' +', ' ', word2)
        # Remove whitespaces from start/end.
        word1 = word1.strip()
        word2 = word2.strip()
        # Check if similarity is above the given threshold.
        return SequenceMatcher(None, word1, word2).ratio() > minimal_similarity


if __name__ == '__main__':
    # Example Usage:
    if RedundancyHandler.areSimilar("Oh Baby", "O  baby! ;", 0.9):
        print "Similar"
    else:
        print "Not similar"
    if RedundancyHandler.areSimilar("Oh Baby", "Oh Mama", 0.9):
        print "Similar"
    else:
        print "Not similar"
