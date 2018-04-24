from nltk.stem import PorterStemmer
import time
import re

from BugSimilarityScoreCalculator import BugSimilarityScoreCalculator
from CosineSimilarityCalculator import CosineSimilarityCalculator
from DataSetFieldEnum import DataSetFieldEnum
import Metrics

from DocumentSpaceCreator import DocumentSpaceCreator
from FileSizeScoreCalculator import FileSizeScoreCalculator
from Util import Util

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()
ranks_file = open('ranks_file.txt', 'w')


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

        rVSM_nomalized = Util.normalization(data[DataSetFieldEnum.rVSMScore], rVSMz_max, rVSMz_min)
        final_rank += (1 - alpha) * rVSM_nomalized

        simi_nomalized = Util.normalization(data[DataSetFieldEnum.simi_score], semi_score_max, semi_score_min)
        final_rank += alpha * simi_nomalized

        dataset[key][DataSetFieldEnum.final_rank] = final_rank


def get_bug_report_cosine_similarity(dataset, source_code_list, cos_simi, max_word_count, min_word_count):
    rVSMz_min = 0
    rVSMz_max = 0.0
    file_size_score_calculator = FileSizeScoreCalculator()
    for i in range(len(cos_simi)):
        file = source_code_list[i].file_path
        cosine_score = cos_simi[i]
        size_score = file_size_score_calculator.calculate_file_size_score(source_code_list[i].word_count, max_word_count, min_word_count)
        rVSMScore = size_score * cosine_score

        if file not in dataset:
            dataset[file] = [rVSMScore, 0.0, 0.0]
        else:
            dataset[file][DataSetFieldEnum.rVSMScore] += rVSMScore

        if dataset[file][DataSetFieldEnum.rVSMScore]> rVSMz_max:
            rVSMz_max = dataset[file][DataSetFieldEnum.rVSMScore]

        if dataset[file][DataSetFieldEnum.rVSMScore]< rVSMz_min:
            rVSMz_min = dataset[file][DataSetFieldEnum.rVSMScore]
    return rVSMz_max, rVSMz_min


def save_ranks_to_file(bug_report, dataset):
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    ranks_file.write("Bug ID: ")
    ranks_file.write(bug_report.id)
    ranks_file.write("\n")

    rank_first_file = -1
    files_binary_relevance = []
    did_locate_bug = False
    count = 0

    for key, value in sorted(dataset.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank], reverse=True):
        # rVSM - SemiScore - FinalScore - FileName"
        print(value, key)

        count += 1
        if count > 10:  # 20
            break

        ranked = False
        for file_name in bug_report.fixed_files:
            if file_name == key:
                ranked = True

        top = " 20 "
        if count == 1:
            top = " 1 "
        elif 1 < count <= 5:
            top = " 5 "
        elif count > 5:
            top = " 10 "

        ranks_file.write("TOP " + top + " | " if ranked else "")
        ranks_file.write(" | ".join(str(i) for i in value))
        ranks_file.write(" ")
        ranks_file.write(key)
        ranks_file.write("\n")

        files_binary_relevance.append(1 if ranked else 0)

        if not did_locate_bug and ranked and count <= 10:
            did_locate_bug = True
            rank_first_file = count

        # print("[{0:.8f}|{0:.8f}|{0:.8f}]".format(value[DataSetField.rVSMScore],value[DataSetField.simi_score],value[DataSetField.final_rank]),key)
    ranks_file.write("\n")
    ranks_file.write("SUCCESSFULLY LOCATED BUG! " if did_locate_bug else "")
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    return rank_first_file, files_binary_relevance


def localize_bugs(current_bug_report, source_code_list, bug_report_list, dataset):
    bug_report_corpus = current_bug_report.content_corpus
    source_code_corpus = []
    cosine_similarity_calculator = CosineSimilarityCalculator()
    bug_similarity_score_calculator = BugSimilarityScoreCalculator()

    max_file_word_count, min_file_word_count = get_max_min_file_size(source_code_corpus, source_code_list)

    query = bug_report_corpus
    documents = source_code_corpus

    # 0: Cosine Similarity (VSM)
    cosine_similarity = cosine_similarity_calculator.compute_cosine_similarity(query, documents)

    # 1: Cosine Similarity for a bug report with source code file size (rVSM)
    rVSMz_max, rVSMz_min = get_bug_report_cosine_similarity(dataset, source_code_list, cosine_similarity,
                                                            max_file_word_count, min_file_word_count)

    # 2: Cosine Similarity for a bug report with the rest of bug reports (SIMI_SCORE)
    semi_score_max, semi_score_min = bug_similarity_score_calculator.get_similar_bug_report_cosine_similarity(dataset, current_bug_report,
                                                                              bug_report_list)

    # 3: Combine 1 and 2
    combine_ranks(0.2, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max)

    # print results in file
    first_file_pos_ranked, files_binary_relevance = save_ranks_to_file(current_bug_report, dataset)
    return first_file_pos_ranked, files_binary_relevance


def main():
    # This is the dataset structure {file_path, [rVSMScore - simiScore - Final Rank]}
    dataset = {}
    start_time = time.time()

    dsc = DocumentSpaceCreator()
    source_code_list = dsc.parse_source_code()
    bug_report_list = dsc.parse_bug_reports()
    print("JAVA FILES  = ", len(source_code_list))
    print("BUG REPORTS = ", len(bug_report_list))

    # metrics
    files_pos_ranked = []
    binary_relevance_list = []

    # FORM 1
    # Compute for each bug report
    # for i in range(len(bug_report_list)):
    #     current_bug_report = bug_report_list[i]
    #     dataset = {}
    #
    #     first_file_pos_ranked, files_binary_relevance = localize_bugs(current_bug_report, source_code_list, bug_report_list, dataset)
    #
    #     files_pos_ranked.append(first_file_pos_ranked)
    #     binary_relevance_list.append(files_binary_relevance)
    # END FORM 1

    # FORM 2
    # Compute for ONE bug report
    current_bug_report = bug_report_list[0]
    first_file_pos_ranked, files_binary_relevance = localize_bugs(current_bug_report, source_code_list, bug_report_list,
                                                                  dataset)

    files_pos_ranked.append(first_file_pos_ranked)
    binary_relevance_list.append(files_binary_relevance)
    # END FORM 2

    # METRICS....
    mean_reciprocal_rank = Metrics.mean_reciprocal_rank(files_pos_ranked, len(bug_report_list))
    mean_average_precision = Metrics.mean_average_precision(binary_relevance_list)

    print("---- METRICS ---- ")
    print("MRR (Mean Reciprocal Rank)   = ", mean_reciprocal_rank)
    print("MAP (Mean Average Precision) = ", mean_average_precision)

    ranks_file.close()
    e = int(time.time() - start_time)
    print('{:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))


if __name__ == "__main__":
    main()
