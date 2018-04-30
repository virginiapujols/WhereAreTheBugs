from DataSetFieldEnum import DataSetFieldEnum
from FileSizeScoreCalculator import FileSizeScoreCalculator


class RVSMCalculator:

    def __init__(self,dataset):
        self.rVSMz_min = 0
        self.rVSMz_max = 0
        self.dataset = dataset

    def calculate(self, cos_simi):
        file_size_score_calculator = FileSizeScoreCalculator()
        for i in range(len(cos_simi)):
            file = self.dataset.source_code_list[i].file_path
            file_word_count = self.dataset.source_code_list[i].word_count
            cosine_score = cos_simi[i]
            size_score = file_size_score_calculator.calculate_file_size_score(file_word_count, self.dataset.max_file_word_count, self.dataset.min_file_word_count)

            rVSMScore = size_score * cosine_score
            #rVSMScore = cosine_score

            if file not in self.dataset.results:
                self.dataset.results[file] = [0.0, 0.0, 0.0]
                self.dataset.results[file][DataSetFieldEnum.rVSMScore] += rVSMScore
            else:
                self.dataset.results[file][DataSetFieldEnum.rVSMScore] += rVSMScore  # WHY IS USING += instead of just equal

            if self.dataset.results[file][DataSetFieldEnum.rVSMScore] > self.rVSMz_max:
                self.rVSMz_max = self.dataset.results[file][DataSetFieldEnum.rVSMScore]

            if self.dataset.results[file][DataSetFieldEnum.rVSMScore] < self.rVSMz_min:
                self.rVSMz_min = self.dataset.results[file][DataSetFieldEnum.rVSMScore]

