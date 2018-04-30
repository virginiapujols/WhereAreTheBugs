import numpy as np


class Metrics:
    def __init__(self,dataset):
        self.dataset = dataset

    def calculate(self):
        mean_reciprocal_rank = self.mean_reciprocal_rank()
        mean_average_precision = self.mean_average_precision(self.dataset.binary_relevance_list)

        print("\n")
        print("---- METRICS ---- ")
        print("TOP N RANK [TOP1, TOP5, TOP10] = ", self.dataset.top_n_rank_list)
        print("MRR (Mean Reciprocal Rank)     = ", mean_reciprocal_rank)
        print("MAP (Mean Average Precision)   = ", mean_average_precision)

    def mean_reciprocal_rank(self,):
        rank_list = self.dataset.files_pos_ranked
        bug_report_size = self.dataset.get_bug_report_list_lenght()
        sum_reciprocal_ranks = 0
        for rank in rank_list:
            sum_reciprocal_ranks += 1 / rank

        mean_rank = sum_reciprocal_ranks / bug_report_size
        return mean_rank

    def mean_average_precision(self, rs):
        """Score is mean average precision

        Relevance is binary (nonzero is relevant).

        rs = [[1, 1, 0, 1, 0, 1, 0, 0, 0, 1]]
        self.mean_average_precision(rs)
        0.78333333333333333
        rs = [[1, 1, 0, 1, 0, 1, 0, 0, 0, 1], [0]]
        self.mean_average_precision(rs)
        0.39166666666666666

        Args:
            rs: Iterator of relevance scores (list or numpy) in rank order
                (first element is the first item)

        Returns:
            Mean average precision
        """
        return np.mean([self.average_precision(r) for r in rs])

    def average_precision(self, r):
        """Score is average precision (area under PR curve)

        Relevance is binary (nonzero is relevant).

        r = [1, 1, 0, 1, 0, 1, 0, 0, 0, 1]
        delta_r = 1. / sum(r)
        sum([sum(r[:x + 1]) / (x + 1.) * delta_r for x, y in enumerate(r) if y])
        0.7833333333333333
        self.average_precision(r)
        0.78333333333333333

        Args:
            r: Relevance scores (list or numpy) in rank order
                (first element is the first item)

        Returns:
            Average precision
        """
        r = np.asarray(r) != 0
        out = [self.precision_at_k(r, k + 1) for k in range(r.size) if r[k]]
        if not out:
            return 0.
        return np.mean(out)

    def precision_at_k(self, r, k):
        """Score is precision @ k

        Relevance is binary (nonzero is relevant).

         r = [0, 0, 1]
        self.precision_at_k(r, 1)
        0.0
        self.precision_at_k(r, 2)
        0.0
        self.precision_at_k(r, 3)
        0.33333333333333331
        self.precision_at_k(r, 4)
        Traceback (most recent call last):
            File "<stdin>", line 1, in ?
        ValueError: Relevance score length < k


        Args:
            r: Relevance scores (list or numpy) in rank order
                (first element is the first item)

        Returns:
            Precision @ k

        Raises:
            ValueError: len(r) must be >= k
        """
        assert k >= 1
        r = np.asarray(r)[:k] != 0
        if r.size != k:
            raise ValueError('Relevance score length < k')
        return np.mean(r)
