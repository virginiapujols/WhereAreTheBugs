from VSMSimilarityCalculator import VSMSimilarityCalculator
from DataSetFieldEnum import DataSetFieldEnum


class BugSimilarityScoreCalculator:

    def calculate_bug_similarity(self, actual_bug_report, bug_report_list):
        semi_score_dictionary = {}
        calc = VSMSimilarityCalculator()
        for bug_report in bug_report_list:
            if actual_bug_report != bug_report:
                similarity_between_reports = calc.VSMSimilarityCalculator(actual_bug_report.content_corpus, [bug_report.content_corpus])[0]
                files_count = len(bug_report.fixed_files)
                simi_score = similarity_between_reports / files_count

                if simi_score != 0:
                    for fixed_file in bug_report.fixed_files:
                        if fixed_file not in semi_score_dictionary:
                            semi_score_dictionary[fixed_file] = simi_score
                        else:
                            semi_score_dictionary[fixed_file] += simi_score

        #for key, value in semi_score.items():
        #    print(key, value)

        return semi_score_dictionary


    def get_similar_bug_report_cosine_similarity(self, dataset, current_bug_report, bug_report_list):
        semi_score_min = 1
        semi_score_max = -1

        semi_score_dictionary = self.calculate_bug_similarity(current_bug_report, bug_report_list)
        for file, score in semi_score_dictionary.items():
            if file not in dataset:
                dataset[file] = [0.0, score, 0.0]
            else:
                dataset[file][DataSetFieldEnum.simi_score] += score

            if dataset[file][DataSetFieldEnum.simi_score] > semi_score_max:
                semi_score_max = dataset[file][DataSetFieldEnum.simi_score]

            if dataset[file][DataSetFieldEnum.simi_score] < semi_score_min:
                semi_score_min = dataset[file][DataSetFieldEnum.simi_score]

        return semi_score_max, semi_score_min
