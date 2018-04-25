from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from FileSizeScoreCalculator import FileSizeScoreCalculator
from StopWord import StopWord


class VSMSimilarityCalculator:
    def __init__(self,attr_analyzer__min_n=1, stop_words=StopWord.java_keywords + StopWord.english_words):
        self.count_vectorizer = CountVectorizer(min_df=attr_analyzer__min_n, stop_words=stop_words)

    def VSMSimilarityCalculator_old(self, query_, document):
        # Attributes
        query = [query_]

        # Learn Vocabulary
        self.count_vectorizer.fit(query)

        # Create vocabulary index
        frequency_term_matrix_query = self.count_vectorizer.transform(query)
        frequency_term_matrix_documents = self.count_vectorizer.transform(document)

        # Calculate tf-idf
        weight_matrix_documents = self.calculate_weight(frequency_term_matrix_query)
        weight_matrix_query = self.calculate_weight(frequency_term_matrix_documents)

        # Calculating similarity
        similarity = self.calculate_similarity(weight_matrix_query, weight_matrix_documents)
        similarity_score = similarity[0]

        print("================frequency_term_matrix_query===================")
        print(frequency_term_matrix_query.todense())

        print("================frequency_term_matrix_documents===================")
        print(frequency_term_matrix_documents.todense())

        #self.print_VSMSimilarityCalculator(frequency_term_matrix_query,self.count_vectorizer.stop_words,self.count_vectorizer.vocabulary_,frequency_term_matrix_documents)
        return similarity_score

    def VSMSimilarityCalculator(self, query, document):
        # Attributes
        stop_words = StopWord.java_keywords + StopWord.english_words
        documents = [query] + document

        tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words, sublinear_tf=True)
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        similarity_scores = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix[1:])
        return list(similarity_scores[0])

    def calculate_weight(self,frequency_term_matrix_documents):
        return self.calculate_tf_idf(frequency_term_matrix_documents, norm='l2')

    def calculate_tf_idf(self, frequency_term_matrix_documents, norm='l2'):
        tf_idf_transformer_documents = TfidfTransformer(norm)
        tf_idf_transformer_documents.fit(frequency_term_matrix_documents)
        tf_idf_matrix_source_code = tf_idf_transformer_documents.transform(frequency_term_matrix_documents)
        return tf_idf_matrix_source_code

    def calculate_similarity(self, weight_matrix_query, weight_matrix_documents):
        return cosine_similarity(weight_matrix_query, weight_matrix_documents)

    def print_VSMSimilarityCalculator(self, frequency_term_matrix_documents, stop_words, vocabulary, frequency_term_matrix_source_code):
        print(' -- -- Matrix dense -- -- ')
        print(frequency_term_matrix_documents.todense())

        print(" -- -- Dictionary in count_vectorizer object -- -- ")
        print(stop_words)

        print(" -- -- Stop words in count_vectorizer object -- -- ")
        print(vocabulary)

        print(' -- -- Matrix -- -- ')
        print(frequency_term_matrix_source_code)
