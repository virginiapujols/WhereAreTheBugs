from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity


def compute_cosine_similarity_test():
    # Documents
    bug_report = ["The sky is blue."]
    source_code_set = ["The sun in the sky is bright.",
                       "We can see the shining sun, the bright sun.",
                       "I can see the  sun, the sky blue  sun."]

    ''' Calculating term frequency '''
    # Attributes
    attr_set_stop_word = ['.', 'we', 'in', 'the', 'is', 'all', 'six', 'less', 'being', 'indeed', 'over', 'move',
                          'anyway', 'four', 'not', 'own', 'through', 'yourselves']
    attr_analyzer__min_n = 1

    # Creating CountVectorizer to create the vocabulary index
    count_vectorizer = CountVectorizer(min_df=attr_analyzer__min_n, stop_words=attr_set_stop_word)

    # Create vocabulary index
    count_vectorizer.fit_transform(bug_report)
    frequency_term_matrix_bug_report = count_vectorizer.transform(bug_report)
    frequency_term_matrix_source_code = count_vectorizer.transform(source_code_set)

    # Printing results
    print(" -- -- Dictionary in count_vectorizer object -- -- ")
    print(count_vectorizer.stop_words)

    print(" -- -- Stop words in count_vectorizer object -- -- ")
    print(count_vectorizer.vocabulary_)

    print(' -- -- Matrix -- -- ')
    print(frequency_term_matrix_source_code)

    print(' -- -- Matrix dense -- -- ')
    print(frequency_term_matrix_source_code.todense())

    ''' Calculating tf-idf source Code'''
    print(' -- -- tf-idf Source Code -- -- ')
    tf_idf_source_code = TfidfTransformer(norm='l2')
    tf_idf_source_code.fit(frequency_term_matrix_source_code)
    # print('IDF = ', tf_idf.idf_)
    tf_idf_matrix_source_code = tf_idf_source_code.transform(frequency_term_matrix_source_code)
    print(tf_idf_matrix_source_code.todense())

    ''' Calculating tf-idf Bug Report'''
    print(' -- -- tf-idf Bug Report -- -- ')
    tf_idf_bug_report = TfidfTransformer(norm='l2')
    tf_idf_bug_report.fit(frequency_term_matrix_bug_report)
    # print('IDF = ', tf_idf.idf_)
    tf_idf_matrix_bug_report = tf_idf_bug_report.transform(frequency_term_matrix_bug_report)
    print(tf_idf_matrix_bug_report.todense())

    ''' Cosine Similarity '''
    print(' -- -- Cosine Similarity -- -- ')
    cos_simi = cosine_similarity(tf_idf_matrix_bug_report, tf_idf_matrix_source_code)
    print(cos_simi)

    ''' Associate similarity score with corresponding source code '''
    cos_simi_dict = {}
    i = 0
    for simi in cos_simi[0]:
        print("cos_simi =", simi)
        cos_simi_dict[simi] = source_code_set[i]
        i += 1
    print(cos_simi_dict)