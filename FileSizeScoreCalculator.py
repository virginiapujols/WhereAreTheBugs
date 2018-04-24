import math

from Util import Util


class FileSizeScoreCalculator:
    def __init__(self):
        self.x_min = 0.00
        self.x_max = 0.00
        self.size_list_source_code = []

    def max_and_min_number_of_term(self):
        x_max = 0.0
        x_min = 0.0

    def normalization(self, x):
        return (x - self.x_min) / (self.x_max - self.x_min)

    def get_terms_in_file(self):
        return 0.0

    def add_to_size_list_from_content(self, content):
        self.size_list_source_code.append(content.length())


    def calculate_score(self, number_of_terms):
        return 1 / (1 + math.e ** (-1 * self.normalization(number_of_terms)))


def calculate_file_size_score(number_of_terms, max, min):
    return 1 / (1 + math.e ** (-1 * Util.normalization(number_of_terms, max, min)))