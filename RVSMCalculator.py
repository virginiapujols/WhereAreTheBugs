from DataSetFieldEnum import DataSetFieldEnum
from FileSizeScoreCalculator import FileSizeScoreCalculator


class RVSMCalculator:
    # def get_max_min_file_size(self, source_code_list):
    #     max_file_word_count = -1
    #     min_file_word_count = 1000000
    #     for current_file in source_code_list:
    #         if current_file.word_count > max_file_word_count:
    #             max_file_word_count = current_file.word_count
    #         if current_file.word_count < min_file_word_count:
    #             min_file_word_count = current_file.word_count
    #
    #     return max_file_word_count, min_file_word_count


    def get_bug_report_cosine_similarity(self, dataset, source_code_list, cos_simi, max_word_count, min_word_count):
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