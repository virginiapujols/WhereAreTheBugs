from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import xml.etree.ElementTree as ET
import math
import time
import os
import fnmatch
import re
from BugReport import BugReport
from SourceCodeFile import SourceCodeFile
from StopWord import StopWord
from FileSizeScoreCalculator import FileSizeScoreCalculator
import Metrics

SOURCE_CODE_PATH = "/Users/virginia/Documents/RIT/SEMESTER 2/SWEN 749 Evolution/Final Project"
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()
ranks_file = open('ranks_file.txt', 'w')


class DataSetField:
    rVSMScore = 0
    simi_score = 1
    final_rank = 2


# Reads a list of bug reports from XML.
# @return List of BugReport objects with report info.
# Includes the stemmed words in @content_corpus
def parse_bug_reports():
    tree = ET.parse('data/SWTBugRepository.xml')
    root = tree.getroot()
    reports = []
    for bug_element in root:
        bug_id = bug_element.get('id')
        bug_sum = ""
        bug_desc = ""
        bug_files = []

        bug_info = bug_element.findall('buginformation')
        for info in bug_info:
            for node in info.getiterator():
                # print(node.tag, node.attrib, node.text)
                if node.text and node.tag == 'summary':
                    bug_sum = node.text
                if node.text and node.tag == 'description':
                    bug_desc = node.text

        for node_files in bug_element.findall('fixedFiles'):
            for node_file in node_files.getiterator():
                if node_file.tag == 'file':
                    # print(node_file.tag, node_file.attrib, node_file.text)
                    bug_files.append(node_file.text)

        # print("bug_id = ", bug_id, "bug_sum = ", bug_sum,
        #       "\nFiles ", bug_files,
        #       "\n----------\n")

        # Extract stemmed words from bug report
        content = ' '.join([bug_sum, bug_desc])
        bug_report_corpus = create_corpus(content)
        reports.append(BugReport(bug_id, bug_sum, bug_desc, bug_report_corpus, bug_files))
    return reports


# Search all .java files, obtain the source code content.
# @return [KEY,VAL] = {KEY = file path, VAL = stemmed words of source file}
def parse_source_code():
    java_files = []
    for root, dir_names, file_names in os.walk("/Users/virginia/Documents/RIT/SEMESTER 2/SWEN 749 Evolution/Final Project/code/test_source_code"):
        # os.walk(SOURCE_CODE_PATH):
        # os.walk("/Users/virginia/Documents/RIT/SEMESTER 2/SWEN 749 Evolution/Final Project/code/test_source_code"):
        for filename in fnmatch.filter(file_names, "*.java"):
            java_files.append(os.path.join(root, filename))

    print("java files = ", len(java_files))
    data = []
    for file in java_files:
        file_content = open(file, 'r', errors='ignore').read()
        head, tail = os.path.split(file)
        package_line = [line for line in file_content.split('\n') if "package" in line]
        if len(package_line) > 0:
            package_line = package_line[0].replace('package ', '').replace(';', '')
            full_class_package = package_line + '.' + tail

            # Extract stemmed words from source code
            source_code_corpus = create_corpus(file_content)
            word_count = len(re.findall(r'\w+', source_code_corpus))
            data.append(SourceCodeFile(full_class_package, source_code_corpus, word_count))

        # try:
        # except:
        #     print("Error: Something wrong occurred opening ", file)

    return data


# Clean up the content of an input text.
# Separates composed words, removes stop words and takes its root element
# @param content: text be stemmed
# @return stemmed text
def create_corpus(content):
    # separate composed words (ClassName|class_name...)
    content = first_cap_re.sub(r'\1_\2', content)
    content = all_cap_re.sub(r'\1_\2', content)
    content = content.replace("_", " ").lower()

    words = word_tokenize(content)
    # print("Tokenizing ", len(words), " words")
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


def compute_cosine_similarity(bug_report_corpus, source_code_corpus):
    # Attributes
    bug_report_corpus = [bug_report_corpus]
    attr_set_stop_word = StopWord.java_keywords + StopWord.english_words
    attr_analyzer__min_n = 1

    # Creating CountVectorizer to create the vocabulary index
    count_vectorizer = CountVectorizer(min_df=attr_analyzer__min_n, stop_words=attr_set_stop_word)

    # Create vocabulary index
    count_vectorizer.fit_transform(bug_report_corpus)
    frequency_term_matrix_bug_report = count_vectorizer.transform(bug_report_corpus)
    frequency_term_matrix_source_code = count_vectorizer.transform(source_code_corpus)

    # get document sizes
    file_size_score_calculator = FileSizeScoreCalculator()


    for row in frequency_term_matrix_source_code:
        file_size_score_calculator.size_list_source_code.append(sum(row))


    # Printing results
    # print(" -- -- Dictionary in count_vectorizer object -- -- ")
    # print(count_vectorizer.stop_words)
    #
    # print(" -- -- Stop words in count_vectorizer object -- -- ")
    # print(count_vectorizer.vocabulary_)
    #
    # print(' -- -- Matrix -- -- ')
    # print(frequency_term_matrix_source_code)
    #
    # print(' -- -- Matrix dense -- -- ')
    # print(frequency_term_matrix_source_code.todense())

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
    # print(cos_simi)

    ''' Associate similarity score with corresponding source code '''
    similarity_score = cos_simi[0]

    # Returns the score of the source_code_corpus in the same order it came
    # e.g: score0 - file0, score1 - file1 and so on...
    return similarity_score


def normalization(x, max, min):
    return (x - min) / (max - min)


def calculate_file_size_score(number_of_terms, max, min):
    return 1 / (1 + math.e ** (-1 * normalization(number_of_terms, max, min)))


def calculate_bug_similarity(actual_bug_report, bug_report_list):
    semi_score_dictionary = {}
    score = 0.0
    for bug_report in bug_report_list:
        if actual_bug_report != bug_report:
            score = compute_cosine_similarity(actual_bug_report.content_corpus, [bug_report.content_corpus])[0]/len(bug_report.fixed_files)

            if score != 0:
                for fixed_file in bug_report.fixed_files:
                    if fixed_file not in semi_score_dictionary:
                        semi_score_dictionary[fixed_file] = score
                    else:
                        semi_score_dictionary[fixed_file] += score

    #for key, value in semi_score.items():
    #    print(key, value)

    return semi_score_dictionary


def get_max_min_file_size(source_code_corpus, source_code_list):
    max_file_word_count = -1
    min_file_word_count = 1000000
    for current_file in source_code_list:
        source_code_corpus.append(current_file.content_corpus)
        if current_file.word_count > max_file_word_count:
            max_file_word_count = current_file.word_count
        if current_file.word_count < min_file_word_count:
            min_file_word_count = current_file.word_count

    return max_file_word_count, min_file_word_count


def combine_ranks(alpha, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max):
    for key, data in dataset.items():
        final_rank = 0

        rVSM_nomalized = normalization(data[DataSetField.rVSMScore], rVSMz_max, rVSMz_min)
        final_rank += (1 - alpha) * rVSM_nomalized

        simi_nomalized = normalization(data[DataSetField.simi_score], semi_score_max, semi_score_min)
        final_rank += alpha * simi_nomalized

        dataset[key][DataSetField.final_rank] = final_rank


def get_similar_bug_report_cosine_similarity(dataset, current_bug_report, bug_report_list):
    semi_score_min = 0
    semi_score_max = 0.0

    semi_score_dictionary = calculate_bug_similarity(current_bug_report, bug_report_list)
    for file, score in semi_score_dictionary.items():
        if file not in dataset:
            dataset[file] = [0.0, score, 0.0]
        else:
            dataset[file][DataSetField.simi_score] += score

        if dataset[file][DataSetField.simi_score] > semi_score_max:
            semi_score_max = dataset[file][DataSetField.simi_score]

        if dataset[file][DataSetField.simi_score] < semi_score_min:
            semi_score_min = dataset[file][DataSetField.simi_score]

    return semi_score_max, semi_score_min


def get_bug_report_cosine_similarity(dataset, source_code_list, cos_simi, max_word_count, min_word_count):
    rVSMz_min = 0
    rVSMz_max = 0.0
    for i in range(len(cos_simi)):
        file = source_code_list[i].file_path
        cosine_score = cos_simi[i]
        size_score = calculate_file_size_score(source_code_list[i].word_count, max_word_count, min_word_count)
        rVSMScore = size_score * cosine_score

        if file not in dataset:
            dataset[file] = [rVSMScore, 0.0, 0.0]
        else:
            dataset[file][DataSetField.rVSMScore] += rVSMScore

        if dataset[file][DataSetField.rVSMScore]> rVSMz_max:
            rVSMz_max = dataset[file][DataSetField.rVSMScore]

        if dataset[file][DataSetField.rVSMScore]< rVSMz_min:
            rVSMz_min = dataset[file][DataSetField.rVSMScore]
    return rVSMz_max, rVSMz_min


def save_ranks_to_file(bug_report, dataset):
    # rVSM - SemiScore - FinalScore - FileName"
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    ranks_file.write("Bug ID: ")
    ranks_file.write(bug_report.id)
    ranks_file.write("\n")

    rank_first_file = -1
    did_locate_bug = False
    count = 0

    for key, value in sorted(dataset.items(), key=lambda e: e[1][DataSetField.final_rank], reverse=True):
        count += 1
        if count > 20:
            break

        ranked = False
        for file_name in bug_report.fixed_files:
            if file_name == key:
                ranked = True

        top = " 20 "
        if count == 1:
            top = " 1 "
        elif count > 1 <= 5:
            top = " 5 "
        elif count > 5 <= 10:
            top = " 10 "

        ranks_file.write("RANKED " + top + " | " if ranked else "")
        ranks_file.write(" | ".join(str(i) for i in value))
        ranks_file.write(" ")
        ranks_file.write(key)
        ranks_file.write("\n")

        if not did_locate_bug and ranked and count <= 10:
            did_locate_bug = True
            rank_first_file = count

        # print("[{0:.8f}|{0:.8f}|{0:.8f}]".format(value[DataSetField.rVSMScore],value[DataSetField.simi_score],value[DataSetField.final_rank]),key)
    ranks_file.write("\n")
    ranks_file.write("SUCCESSFULLY LOCATED BUG! " if did_locate_bug else "")
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    return rank_first_file

def main():
    # This is the dataset structure {file_path, [rVSMScore - simiScore - Final Rank]}
    dataset = {}
    start_time = time.time()

    source_code_list = parse_source_code()
    bug_report_list = parse_bug_reports()

    # metrics
    files_pos_ranked = []

    # Compute for each bug report
    for i in range(len(bug_report_list)):
        current_bug_report = bug_report_list[i]
        bug_report_corpus = current_bug_report.content_corpus
        source_code_corpus = []

        max_file_word_count, min_file_word_count = get_max_min_file_size(source_code_corpus, source_code_list)

        query = bug_report_corpus
        documents = source_code_corpus

        # 0: Cosine Similarity (VSM)
        cosine_similarity = compute_cosine_similarity(query, documents)

        # 1: Cosine Similarity for a bug report with source code file size (rVSM)
        rVSMz_max, rVSMz_min = get_bug_report_cosine_similarity(dataset, source_code_list, cosine_similarity,
                                                                max_file_word_count, min_file_word_count)

        # 2: Cosine Similarity for a bug report with the rest of bug reports (SIMI_SCORE)
        semi_score_max, semi_score_min = get_similar_bug_report_cosine_similarity(dataset, current_bug_report, bug_report_list)

        # 3: Combine 1 and 2
        combine_ranks(0.2, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max)

        # print results in file
        first_file_pos_ranked = save_ranks_to_file(current_bug_report, dataset)
        files_pos_ranked.append(first_file_pos_ranked)

    # METRICS....
    mean_reciprocal_rank = Metrics.mean_reciprocal_rank(files_pos_ranked, len(bug_report_list))

    print("---- METRICS ---- ")
    print("MRR (Mean Reciprocal Rank) = ", mean_reciprocal_rank)

    ranks_file.close()
    e = int(time.time() - start_time)
    print('{:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))


if __name__ == "__main__":
    main()
