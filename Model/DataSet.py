from Model.DocumentSpaceCreator import DocumentSpaceCreator

class DataSet:
    def __init__(self):
        self.source_code_list = []
        self.bug_report_list = []
        self.results = {}
        self.top_n_rank_list = []
        self.files_pos_ranked = []
        self.binary_relevance_list = []
        self.source_code_corpus = []
        self.max_file_word_count = 0
        self.min_file_word_count = 0


    def create_document_space(self):
        dsc = DocumentSpaceCreator()
        self.source_code_list = dsc.parse_source_code()
        self.bug_report_list = dsc.parse_bug_reports()
        self.source_code_corpus, self.max_file_word_count, self.min_file_word_count = dsc.get_source_code_corpus_max_min(
            self.source_code_list)

    def get_source_code_list_lenght(self):
        return len(self.source_code_list)

    def get_bug_report_list_lenght(self):
        return len(self.bug_report_list)

    def get_results_items(self):
        self.results.items()

    def reset_calculation_lists(self):
        self.top_n_rank_list = [0, 0, 0]
        self.files_pos_ranked = []
        self.binary_relevance_list = []





