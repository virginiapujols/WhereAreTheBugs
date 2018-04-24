from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

from FileSizeScoreCalculator import FileSizeScoreCalculator
from StopWord import StopWord

class CosineSimilarityCalculator:
    def compute_cosine_similarity(self, query_, document):
        # Attributes
        query = [query_]
        attr_set_stop_word = StopWord.java_keywords + StopWord.english_words
        attr_analyzer__min_n = 1

        # Creating CountVectorizer to create the vocabulary index
        count_vectorizer = CountVectorizer(min_df=attr_analyzer__min_n, stop_words=attr_set_stop_word)

        # Create vocabulary index
        count_vectorizer.fit_transform(query)
        frequency_term_matrix_bug_report = count_vectorizer.transform(query)
        frequency_term_matrix_source_code = count_vectorizer.transform(document)

        # get document sizes
        file_size_score_calculator = FileSizeScoreCalculator()


        for row in frequency_term_matrix_source_code:
            file_size_score_calculator.size_list_source_code.append(sum(row))


        #Printing results
        #print(" -- -- Dictionary in count_vectorizer object -- -- ")
        #print(count_vectorizer.stop_words)

        #print(" -- -- Stop words in count_vectorizer object -- -- ")
        #print(count_vectorizer.vocabulary_)

        #print(' -- -- Matrix -- -- ')
        #print(frequency_term_matrix_source_code)

        print(' -- -- Matrix dense -- -- ')
        print(frequency_term_matrix_source_code.todense())

        ''' Calculating tf-idf source Code'''
        # print(' -- -- tf-idf Source Code -- -- ')
        tf_idf_source_code = TfidfTransformer(norm='l2')
        tf_idf_source_code.fit(frequency_term_matrix_source_code)
        # print('IDF = ', tf_idf.idf_)
        tf_idf_matrix_source_code = tf_idf_source_code.transform(frequency_term_matrix_source_code)
        # print(tf_idf_matrix_source_code.todense())

        ''' Calculating tf-idf Bug Report'''
        # print(' -- -- tf-idf Bug Report -- -- ')
        tf_idf_bug_report = TfidfTransformer(norm='l2')
        tf_idf_bug_report.fit(frequency_term_matrix_bug_report)
        # print('IDF = ', tf_idf.idf_)
        tf_idf_matrix_bug_report = tf_idf_bug_report.transform(frequency_term_matrix_bug_report)
        # print(tf_idf_matrix_bug_report.todense())

        ''' Cosine Similarity '''
        # print(' -- -- Cosine Similarity -- -- ')
        cos_simi = cosine_similarity(tf_idf_matrix_bug_report, tf_idf_matrix_source_code)
        print(cos_simi)

        ''' Associate similarity score with corresponding source code '''
        similarity_score = cos_simi[0]

        # Returns the score of the source_code_corpus in the same order it came
        # e.g: score0 - file0, score1 - file1 and so on...
        return similarity_score