from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from StopWord import StopWord

class VSMSimilarityCalculator:
    def  calculate(self, query, document):
        stop_words = StopWord.java_keywords + StopWord.english_words
        documents = [query] + document
        tfidf_vectorizer = TfidfVectorizer(sublinear_tf=True)
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix[1:])
        return list(similarity_scores[0])

    def print_vsm_similarity_info(self, frequency_term_matrix_documents, stop_words, vocabulary, frequency_term_matrix_source_code):
        print(' -- -- Matrix dense -- -- ')
        print(frequency_term_matrix_documents.todense())

        print(" -- -- Dictionary in count_vectorizer object -- -- ")
        print(stop_words)

        print(" -- -- Stop words in count_vectorizer object -- -- ")
        print(vocabulary)

        print(' -- -- Matrix -- -- ')
        print(frequency_term_matrix_source_code)
