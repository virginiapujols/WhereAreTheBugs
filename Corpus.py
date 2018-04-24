from nltk.tokenize import word_tokenize
from StopWord import StopWord
import re
from nltk.stem import PorterStemmer

SOURCE_CODE_PATH = "/Users/virginia/Documents/RIT/SEMESTER 2/SWEN 749 Evolution/Final Project"
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()


class Corpus:

    # Clean up the content of an input text.
    # Separates composed words, removes stop words and takes its root element
    # @param content: text be stemmed
    # @return stemmed text
    def create_corpus(self,content):
        # separate composed words (ClassName|class_name...)
        content = first_cap_re.sub(r'\1_\2', content)
        content = all_cap_re.sub(r'\1_\2', content)
        content = content.replace("_", " ").lower()

        words = word_tokenize(content)
        print("Tokenizing ", len(words), " words")
        stemmed_words = set()
        for w in words:
            # jump english stop words and java frequently used keywords
            if (w in StopWord.english_words) or (w in StopWord.java_keywords):
                continue

            # reduce words to its root
            porter_stemmer.stem(w)
            stemmed_words.add(w)

        # return stemmed_words
        return ' '.join(stemmed_words)