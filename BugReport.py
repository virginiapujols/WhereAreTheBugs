class BugReport:

    def __init__(self, report_id, title, description, corpus, files):
        self.id = report_id
        self.title = title
        self.description = description
        self.content_corpus = corpus
        self.fixed_files = files

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
