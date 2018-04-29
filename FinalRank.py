from DataSetFieldEnum import DataSetFieldEnum
from Util import Util


class FinalRank:
    def __init__(self, dataset):
        self.dataset = dataset

    def combine_ranks(self, alpha, rvsm_calculator, bug_similarity_calculator):
        for key, data in self.dataset.results.items():
            rVSM_nomalized = Util.normalization(data[DataSetFieldEnum.rVSMScore], rvsm_calculator.rVSMz_max,
                                                rvsm_calculator.rVSMz_min)
            simi_nomalized = Util.normalization(data[DataSetFieldEnum.simi_score],
                                                bug_similarity_calculator.semi_score_max,
                                                bug_similarity_calculator.semi_score_min)

            final_score = (1.0 - alpha) * rVSM_nomalized + alpha * simi_nomalized
            # final_score = (1.0 - alpha) * data[DataSetFieldEnum.rVSMScore] + alpha * data[DataSetFieldEnum.simi_score]
            self.dataset.results[key][DataSetFieldEnum.final_rank] = final_score
