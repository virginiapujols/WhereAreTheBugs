import re

from nltk import PorterStemmer

from BugSimilarityScoreCalculator import BugSimilarityScoreCalculator
from DataSetFieldEnum import DataSetFieldEnum
from FinalRank import FinalRank
from RVSMCalculator import RVSMCalculator
from VSMSimilarityCalculator import VSMSimilarityCalculator

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()
ranks_file = open('ranks_file.txt', 'w')

class BugLocalization:
    def __init__(self,dataset):
        self.dataset = dataset


    def run(self):
        self.dataset.reset_calculation_lists()
        for i in range(self.dataset.get_bug_report_list_lenght()):
            current_bug_report = self.dataset.bug_report_list[i]
            self.dataset.results = {}
            self.localize_bugs(current_bug_report)

            first_file_pos_ranked = self.calculate_rank_first(self.dataset,current_bug_report)
            files_binary_relevance = self.calculate_binary(current_bug_report,self.dataset)
            top_n_rank = self.calculate_tops(current_bug_report,self.dataset)

            self.dataset.files_pos_ranked.append(first_file_pos_ranked)
            self.dataset.binary_relevance_list.append(files_binary_relevance)
            self.dataset.top_n_rank_list = [self.dataset.top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]

    def save_ranks_to_file(self,dataset, bug_report):
        ranks_file.write("\n +++++++++++++++++++++++++++++++++++++ \n")
        ranks_file.write("rVSMScore|simi_score|final_rank|file name \n")
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


    def calculate_binary_tops(self, bug_report, dataset):
        top1_count = 0
        top5_count = 0
        top10_count = 0
        files_binary_relevance = []
        sorted_results10 = sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank],
                                  reverse=True)[:10]
        for count, dict_list in enumerate(sorted_results10, 1):
            ranked = False

            # Evaluate if bug  is in list
            for file_name in bug_report.fixed_files:
                if file_name == dict_list[0]:
                    ranked = True
            if ranked:
                if count == 1:
                    top1_count += 1
                elif 1 < count <= 5:
                    top5_count += 1
                elif 5 < count <= 10:
                    top10_count += 1
            files_binary_relevance.append(1 if ranked else 0)
        return files_binary_relevance, top10_count, top1_count, top5_count

    def calculate_rank_first(self,dataset, bug_report):
        rank_first_file = 0
        did_locate_bug = False
        count = 0
        sorted_results = sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank], reverse=True)

        for key, value in sorted_results:
            count += 1
            ranked = False

            # Evaluate if bug  is in list
            for file_name in bug_report.fixed_files:
                if file_name == key:
                    ranked = True

            if not did_locate_bug and ranked:
                did_locate_bug = True
                rank_first_file = count

        return rank_first_file

    def calculate_tops(self, bug_report, dataset):
        top1_count = 0
        top5_count = 0
        top10_count = 0
        end = False
        sorted_results10 = sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank],
                                  reverse=True)[:10]
        for count, dict_list in enumerate(sorted_results10, 1):
            for file_name in bug_report.fixed_files:
                if not end:
                    if file_name == dict_list[0]:
                        if count == 1:
                            top1_count += 1
                            top5_count += 1
                            top10_count += 1
                            end = True
                        if 1 < count <= 5:
                            top5_count += 1
                            top10_count += 1
                            end = True
                        if 5 < count <= 10:
                            top10_count += 1
                            end = True
        return top1_count, top5_count, top10_count

    def calculate_binary(self, bug_report, dataset):
        files_binary_relevance = []
        sorted_results10 = sorted(dataset.results.items(), key=lambda e: e[1][DataSetFieldEnum.final_rank],
                                  reverse=True)[:10]
        for count, dict_list in enumerate(sorted_results10, 1):
            ranked = False

            # Evaluate if bug  is in list
            for file_name in bug_report.fixed_files:
                if file_name == dict_list[0]:
                    ranked = True
            files_binary_relevance.append(1 if ranked else 0)
        return files_binary_relevance

    def localize_bugs(self, current_bug_report):
        # Creating source code corpus
        bug_report_corpus = current_bug_report.content_corpus

        # 0: Cosine Similarity (VSM)
        cosine_similarity = VSMSimilarityCalculator().calculate(bug_report_corpus, self.dataset.source_code_corpus)

        # 1: Cosine Similarity for a bug report with source code file size (rVSM)
        rvsm_calculator = RVSMCalculator(self.dataset)
        rvsm_calculator.calculate(cosine_similarity)

        # 2: Cosine Similarity for a bug report with the rest of bug reports (SIMI_SCORE)
        bug_similarity_calculator = BugSimilarityScoreCalculator(self.dataset)
        bug_similarity_calculator.get_similar_bug_report_cosine_similarity(current_bug_report)

        # 3: Combine 1 and 2
        rank_combinator = FinalRank(self.dataset)
        rank_combinator.combine_ranks(0.25, rvsm_calculator,bug_similarity_calculator)

        # print results in file
        #print(self.dataset.results)
        self.save_ranks_to_file(self.dataset, current_bug_report)