import os
import fnmatch
from  SourceCodeFile import SourceCodeFile
from Corpus import Corpus


class SourceCodeCorpus(Corpus):
    def __init__(self,corpus=[]):
        self.corpus = corpus
        #Corpus.__init__(self)

    def parse_source_code(self,dir_path):
        java_files = []
        for root, dir_names, file_names in os.walk(self.dir_path):
            # os.walk(SOURCE_CODE_PATH):
            for filename in fnmatch.filter(file_names, "*.java"):
                java_files.append(os.path.join(root, filename))

        print("java files = ", len(java_files))
        data = []
        for file in java_files:
            file_content = open(file, 'r', errors='ignore').read()

            # Extract stemmed words from source code
            source_code_corpus = self.create_corpus(file_content)
            self.corpus.append(SourceCodeFile(file, source_code_corpus))

        return data