from nltk.tokenize import word_tokenize
from StopWord import StopWord
import re
from nltk.stem import PorterStemmer
import xml.etree.ElementTree as ET
import os
import fnmatch
from SourceCodeFile import SourceCodeFile
from BugReport import BugReport


# SOURCE_CODE_PATH = "G:\Team Drives\Team Evolution\swt_src"
SOURCE_CODE_PATH = "/Users/virginia/Documents/RIT/SEMESTER 2/SWEN 749 Evolution/Final Project/swt-3.1"
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
porter_stemmer = PorterStemmer()


class DocumentSpaceCreator:

    # Clean up the content of an input text.
    # Separates composed words, removes stop words and takes its root element
    # @param content: text be stemmed
    # @return stemmed text
    def create_corpus(self, content):
        # separate composed words (ClassName|class_name...)
        content = self.preprocess_content(content)
        words = word_tokenize(content)
        stemmed_words = set()

        for w in words:
            # jump english stop words and java frequently used keywords
            if (w in StopWord.english_words) or (w in StopWord.java_keywords):
                continue

            # reduce words to its root
            porter_stemmer.stem(w)
            stemmed_words.add(w)

        # return stemmed_words
        return ' '.join(stemmed_words)

    def preprocess_content(self, content):
        content = first_cap_re.sub(r'\1___\2', content)
        content = all_cap_re.sub(r'\1___\2', content)
        content = content.replace("___", " ")
        content = content.lower()
        return content

    # Reads a list of bug reports from XML.
    # @return List of BugReport objects with report info.
    # Includes the stemmed words in @content_corpus
    def parse_bug_reports(self):
        tree = ET.parse('data/SWTBugRepository.xml')
        root = tree.getroot()
        reports = []
        for bug_element in root:
            bug_id = bug_element.get('id')
            bug_sum = ""
            bug_desc = ""
            bug_files = []

            bug_info = bug_element.findall('buginformation')
            for info in bug_info:
                for node in info.getiterator():
                    # print(node.tag, node.attrib, node.text)
                    if node.text and node.tag == 'summary':
                        bug_sum = node.text
                    if node.text and node.tag == 'description':
                        bug_desc = node.text

            for node_files in bug_element.findall('fixedFiles'):
                for node_file in node_files.getiterator():
                    if node_file.tag == 'file':
                        # print(node_file.tag, node_file.attrib, node_file.text)
                        bug_files.append(node_file.text)

            # print("bug_id = ", bug_id, "bug_sum = ", bug_sum,
            #       "\nFiles ", bug_files,
            #       "\n----------\n")

            # Extract stemmed words from bug report
            content = ' '.join([bug_sum, bug_desc])
            bug_report_corpus = self.create_corpus(content)
            reports.append(BugReport(bug_id, bug_sum, bug_desc, bug_report_corpus, bug_files))
        return reports


    '''
    @Brief Search all .java files, obtain the source code content.
    
    Input: Root directory of the source code directory, 
    return All source code files  
    Related methods:
    create_corpus
    '''
    def parse_source_code(self):
        java_files = []
        for root, dir_names, file_names in os.walk(SOURCE_CODE_PATH):
            for filename in fnmatch.filter(file_names, "*.java"):
                java_files.append(os.path.join(root, filename))

        data = []
        for file in java_files:
            file_content = open(file, 'r', errors='ignore').read()
            head, tail = os.path.split(file)
            package_line = [line for line in file_content.split('\n') if "package" in line]
            if len(package_line) > 0:
                package_line = package_line[0].replace('package ', '').replace(';', '')
                full_class_package = package_line + '.' + tail

                # Extract stemmed words from source code
                source_code_corpus = self.create_corpus(file_content)
                word_count = len(re.findall(r'\w+', source_code_corpus))
                data.append(SourceCodeFile(full_class_package, source_code_corpus, word_count))

            # try:
            # except:
            #     print("Error: Something wrong occurred opening ", file)

        return data