from DataSetFieldEnum import DataSetFieldEnum
from Util import Util


class RankCombinator:
    def combine_ranks(self, alpha, dataset, rVSMz_min, rVSMz_max, semi_score_min, semi_score_max):
        for key, data in dataset.items():
            final_rank = 0

            rVSM_nomalized = Util.normalization(data[DataSetFieldEnum.rVSMScore], rVSMz_max, rVSMz_min)
            final_rank += (1 - alpha) * rVSM_nomalized

            simi_nomalized = Util.normalization(data[DataSetFieldEnum.simi_score], semi_score_max, semi_score_min)
            final_rank += alpha * simi_nomalized

            dataset[key][DataSetFieldEnum.final_rank] = final_rank