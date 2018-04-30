import math

from DataSetFieldEnum import DataSetFieldEnum

from Util import Util


class RVSMCalculator:

    def __init__(self,dataset):
        self.rVSMz_min = 0
        self.rVSMz_max = 0
        self.dataset = dataset

    def calculate(self, cos_simi):
        for i in range(len(cos_simi)):
            file_word_count = self.dataset.source_code_list[i].file_lenght
            cosine_score = cos_simi[i]
            size_score = self.calculate_file_size_score(file_word_count*8.4, self.dataset.max_file_lengh, self.dataset.min_file_lenght)

            rVSMScore = size_score * cosine_score
            self.distribute_size_score(i, rVSMScore)

    def distribute_size_score(self, i, rVSMScore):
        file = self.dataset.source_code_list[i].file_path
        if file not in self.dataset.results:
            self.dataset.results[file] = [0.0, 0.0, 0.0]
            self.dataset.results[file][DataSetFieldEnum.rVSMScore] = rVSMScore
        else:
            self.dataset.results[file][DataSetFieldEnum.rVSMScore] = rVSMScore
        if self.dataset.results[file][DataSetFieldEnum.rVSMScore] > self.rVSMz_max:
            self.rVSMz_max = self.dataset.results[file][DataSetFieldEnum.rVSMScore]
        if self.dataset.results[file][DataSetFieldEnum.rVSMScore] < self.rVSMz_min:
            self.rVSMz_min = self.dataset.results[file][DataSetFieldEnum.rVSMScore]


    def calculate_file_size_score(self, number_of_terms, max, min):
        return 1 / (1 + math.e ** (-1 * Util.normalization(number_of_terms, max, min)))