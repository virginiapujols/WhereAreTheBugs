from BugReport import BugReport

class BugFixingRecencyCalculator:
    '''
    br_set is the set of bug reports for which file source_code was fixed before bug report bug_report_query was created.
    last_bug_report is the most recent previously fixed bug
    '''

    #def calculate(self,bug_report_query, source_code):

    def get_br_set(self,bug_report_query, source_code_file_name, bug_report_list):
        br_set = set()
        for bug_report in bug_report_list:
            if source_code_file_name in bug_report.fixed_files:
                set.add(bug_report)
        return br_set

   # def get_last_bug_report(self,br_set):
    #    for br



