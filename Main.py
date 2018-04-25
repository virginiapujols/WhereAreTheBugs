from nltk.stem import PorterStemmer
import time
import re

from BugSimilarityScoreCalculator import BugSimilarityScoreCalculator
from VSMSimilarityCalculator import VSMSimilarityCalculator
from DataSetFieldEnum import DataSetFieldEnum
from Metrics import Metrics

from DocumentSpaceCreator import DocumentSpaceCreator
from RankCombinator import RankCombinator
from RVSMCalculator import RVSMCalculator

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()
ranks_file = open('ranks_file.txt', 'w')


def save_ranks_to_file(bug_report, dataset):
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    ranks_file.write("Bug ID: ")
    ranks_file.write(bug_report.id)
    ranks_file.write("\n")

    rank_first_file = -1
    top1_count = 0
    top5_count = 0
    top10_count = 0
    files_binary_relevance = []
    did_locate_bug = False
    count = 0

    for key, value in sorted(dataset.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank], reverse=True):
        # rVSM - SemiScore - FinalScore - FileName"
        #print(value, key)

        count += 1
        if count > 10:  # 20
            break

        ranked = False
        for file_name in bug_report.fixed_files:
            if file_name == key:
                ranked = True

        top = ""
        if count == 1:
            top = " 1 "
            top1_count += 1 if ranked else 0
        elif 1 < count <= 5:
            top = " 5 "
            top5_count += 1 if ranked else 0
        elif count > 5:
            top = " 10 "
            top10_count += 1 if ranked else 0

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
    return rank_first_file, files_binary_relevance, [top1_count, top5_count, top10_count]


def localize_bugs(current_bug_report, source_code_list, bug_report_list, dataset):

    # Creating source code corpus
    source_code_corpus, max_file_word_count, min_file_word_count = DocumentSpaceCreator.get_source_code_corpus_max_min(source_code_list)
    bug_report_corpus = current_bug_report.content_corpus

    # 0: Cosine Similarity (VSM)
    cosine_similarity = VSMSimilarityCalculator().VSMSimilarityCalculator(bug_report_corpus, source_code_corpus)

    # 1: Cosine Similarity for a bug report with source code file size (rVSM)
    rVSMz_max, rVSMz_min = RVSMCalculator().get_bug_report_cosine_similarity(dataset, source_code_list, cosine_similarity,
                                                            max_file_word_count, min_file_word_count)

    # 2: Cosine Similarity for a bug report with the rest of bug reports (SIMI_SCORE)
    semi_score_max, semi_score_min = BugSimilarityScoreCalculator().get_similar_bug_report_cosine_similarity(dataset, current_bug_report, bug_report_list)

    # 3: Combine 1 and 2
    RankCombinator().combine_ranks(0.2, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max)

    # print results in file
    first_file_pos_ranked, files_binary_relevance, top_n_rank = save_ranks_to_file(current_bug_report, dataset)
    return first_file_pos_ranked, files_binary_relevance, top_n_rank


def compute_one_bug_report(binary_relevance_list, bug_report_list, files_pos_ranked, source_code_list, top_n_rank_list):
    dataset = {}
    current_bug_report = bug_report_list[0]
    first_file_pos_ranked, files_binary_relevance, top_n_rank = localize_bugs(current_bug_report, source_code_list,
                                                                              bug_report_list, dataset)
    files_pos_ranked.append(first_file_pos_ranked)
    binary_relevance_list.append(files_binary_relevance)
    top_n_rank_list = [top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]
    return top_n_rank_list


def computer_all_bug_reports(binary_relevance_list, bug_report_list, files_pos_ranked, source_code_list, top_n_rank_list):
    for i in range(len(bug_report_list)):
        current_bug_report = bug_report_list[i]
        dataset = {}

        first_file_pos_ranked, files_binary_relevance, top_n_rank = localize_bugs(current_bug_report, source_code_list,
                                                                                  bug_report_list, dataset)

        files_pos_ranked.append(first_file_pos_ranked)
        binary_relevance_list.append(files_binary_relevance)
        top_n_rank_list = [top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]
    return top_n_rank_list


def main():

    start_time = time.time()
    dsc = DocumentSpaceCreator()
    source_code_list = dsc.parse_source_code()
    bug_report_list = dsc.parse_bug_reports()
    print("JAVA FILES  = ", len(source_code_list))
    print("BUG REPORTS = ", len(bug_report_list))

    # metrics
    files_pos_ranked = []
    binary_relevance_list = []
    top_n_rank_list = [0, 0, 0]

    # FORM 1
    # Compute for each bug report
    top_n_rank_list = computer_all_bug_reports(binary_relevance_list, bug_report_list, files_pos_ranked,
                                               source_code_list, top_n_rank_list)

    # Compute for ONE bug report
    # top_n_rank_list = compute_one_bug_report(binary_relevance_list, bug_report_list, files_pos_ranked, source_code_list,
    #                                          top_n_rank_list)

    #print("TOPNRANK [TOP1, TOP5, TOP10] = ", top_n_rank_list)
    # METRICS....
    metric = Metrics()
    metric.calculate(files_pos_ranked,len(bug_report_list),binary_relevance_list,top_n_rank_list)

    ranks_file.close()
    e = int(time.time() - start_time)
    # Elapase Time
    print('\nElapsed Time: {:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))

if __name__ == "__main__":
    main()
