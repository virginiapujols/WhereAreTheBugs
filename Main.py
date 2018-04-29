from nltk.stem import PorterStemmer
import time
import re

from BugSimilarityScoreCalculator import BugSimilarityScoreCalculator
from Model.DataSet import DataSet
from VSMSimilarityCalculator import VSMSimilarityCalculator
from DataSetFieldEnum import DataSetFieldEnum
from Metrics import Metrics

from Model.DocumentSpaceCreator import DocumentSpaceCreator
from RankCombinator import RankCombinator
from RVSMCalculator import RVSMCalculator

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()
ranks_file = open('ranks_file.txt', 'w')


def save_ranks_to_file(dataset, bug_report):
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
    ranks_file.write("Bug ID: ")
    ranks_file.write(bug_report.id)
    ranks_file.write("\n")

    rank_first_file = 0
    top1_count = 0
    top5_count = 0
    top10_count = 0
    files_binary_relevance = []
    did_locate_bug = False
    count = 0

    for key, value in sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank], reverse=True):
        # rVSM - SemiScore - FinalScore - FileName"
        # print(value, key)

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
        elif 1 < count <= 5:
            top = " 5 "
        elif count > 5:
            top = " 10 "

        ranks_file.write("TOP " + top + " | " if ranked else "")
        ranks_file.write(" | ".join(str(i) for i in value))
        ranks_file.write(" ")
        ranks_file.write(key)
        ranks_file.write("\n")

    ranks_file.write("\n")
    ranks_file.write("SUCCESSFULLY LOCATED BUG! " if did_locate_bug else "")
    ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")


def calculate_rank_first_file_and_tops(dataset, bug_report):
    rank_first_file = 0
    top1_count = 0
    top5_count = 0
    top10_count = 0
    files_binary_relevance = []
    did_locate_bug = False
    count = 0

    for key, value in sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank], reverse=True):
        count += 1
        ranked = False

        # Evaluate if bug  is in list
        for file_name in bug_report.fixed_files:
            if file_name == key:
                ranked = True

        if not did_locate_bug and ranked:
            did_locate_bug = True
            rank_first_file = count

        if count <= 10:
            if count == 1:
                top1_count += 1 if ranked else 0
            elif 1 < count <= 5:
                top5_count += 1 if ranked else 0
            elif 5 < count <= 10:
                top10_count += 1 if ranked else 0
            files_binary_relevance.append(1 if ranked else 0)

    return rank_first_file, files_binary_relevance, [top1_count, top5_count, top10_count]


def localize_bugs(dataset, current_bug_report):
    # Creating source code corpus
    source_code_corpus, max_file_word_count, min_file_word_count = DocumentSpaceCreator.get_source_code_corpus_max_min(
        dataset.source_code_list)
    bug_report_corpus = current_bug_report.content_corpus

    # 0: Cosine Similarity (VSM)
    cosine_similarity = VSMSimilarityCalculator().calculate(bug_report_corpus, source_code_corpus)

    # 1: Cosine Similarity for a bug report with source code file size (rVSM)
    rvsm_calculator = RVSMCalculator()
    rvsm_calculator.get_bug_report_cosine_similarity(dataset, cosine_similarity,
                                                     max_file_word_count, min_file_word_count)

    # 2: Cosine Similarity for a bug report with the rest of bug reports (SIMI_SCORE)
    semi_score_max, semi_score_min = BugSimilarityScoreCalculator().get_similar_bug_report_cosine_similarity(
        dataset, current_bug_report )

    # 3: Combine 1 and 2
    RankCombinator().combine_ranks(dataset, 0.2, rvsm_calculator.rVSMz_min, rvsm_calculator.rVSMz_max,
                                   semi_score_min, semi_score_max)

    # print results in file

    save_ranks_to_file(dataset, current_bug_report)


def compute_one_bug_report(binary_relevance_list, bug_report_list, files_pos_ranked, source_code_list, top_n_rank_list):
    dataset = {}
    current_bug_report = bug_report_list[0]
    localize_bugs(source_code_list, current_bug_report)
    first_file_pos_ranked, files_binary_relevance, top_n_rank = calculate_rank_first_file_and_tops(dataset,
                                                                                                   current_bug_report)
    files_pos_ranked.append(first_file_pos_ranked)
    binary_relevance_list.append(files_binary_relevance)
    top_n_rank_list = [top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]
    return top_n_rank_list


def computer_all_bug_reports(dataset):
    top_n_rank_list = [0, 0, 0]
    files_pos_ranked = []
    binary_relevance_list = []
    for i in range(dataset.get_bug_report_list_lenght()):
        current_bug_report = dataset.bug_report_list[i]
        dataset.results = {}
        localize_bugs(dataset, current_bug_report)

        first_file_pos_ranked, files_binary_relevance, top_n_rank = calculate_rank_first_file_and_tops(dataset,
                                                                                                       current_bug_report)

        files_pos_ranked.append(first_file_pos_ranked)
        binary_relevance_list.append(files_binary_relevance)
        top_n_rank_list = [top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]
    return top_n_rank_list, files_pos_ranked, binary_relevance_list


def main():
    # set timer to measure Elapsed Time
    start_time = time.time()

    dataset = DataSet()
    dataset.create_document_space()

    # Parsing documents
    source_code_list = dataset.source_code_list
    bug_report_list = dataset.bug_report_list

    # Printing to output the amount of documents in the document space
    print("JAVA FILES  = ", dataset.get_source_code_list_lenght())
    print("BUG REPORTS = ", dataset.get_bug_report_list_lenght())

    # Compute all bug reports
    top_n_rank_list, files_pos_ranked, binary_relevance_list = computer_all_bug_reports(dataset)

    # Calculating and printing metrics printing metrics
    metric = Metrics()
    metric.calculate(files_pos_ranked, len(bug_report_list), binary_relevance_list, top_n_rank_list)
    print("---top_n_rank_list ---")
    print(files_pos_ranked)

    ranks_file.close()

    # Elapsed Time
    e = int(time.time() - start_time)
    print('\nElapsed Time: {:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))


if __name__ == "__main__":
    main()
