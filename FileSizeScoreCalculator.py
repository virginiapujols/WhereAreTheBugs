import math
from Util import Util


class FileSizeScoreCalculator:
    def __init__(self):
        self.x_min = 0.00
        self.x_max = 0.00
        self.size_list_source_code = []

    def calculate_file_size_score(self, number_of_terms, max, min):
        return 1 / (1 + math.e ** (-1 * Util.normalization(number_of_terms, max, min)))