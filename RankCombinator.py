from DataSetFieldEnum import DataSetFieldEnum
from Util import Util


class RankCombinator:
    def combine_ranks(self, alpha, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max):
        for key, data in dataset.items():
            rVSM_nomalized = Util.normalization(data[DataSetFieldEnum.rVSMScore], rVSMz_max, rVSMz_min)
            simi_nomalized = Util.normalization(data[DataSetFieldEnum.simi_score], semi_score_max, semi_score_min)

            final_score = (1.0 - alpha) * rVSM_nomalized + alpha * simi_nomalized
            # final_score = (1.0 - alpha) * data[DataSetFieldEnum.rVSMScore] + alpha * data[DataSetFieldEnum.simi_score]
            dataset[key][DataSetFieldEnum.final_rank] = final_score
