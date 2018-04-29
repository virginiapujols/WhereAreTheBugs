import time

from BugLocalization import BugLocalization, ranks_file
from Model.DataSet import DataSet
from Metrics import Metrics


# def compute_one_bug_report(binary_relevance_list, bug_report_list, files_pos_ranked, source_code_list, top_n_rank_list):
#     dataset = {}
#     current_bug_report = bug_report_list[0]
#     localize_bugs(source_code_list, current_bug_report)
#     first_file_pos_ranked, files_binary_relevance, top_n_rank = calculate_rank_first_file_and_tops(dataset,
#                                                                                                    current_bug_report)
#     files_pos_ranked.append(first_file_pos_ranked)
#     binary_relevance_list.append(files_binary_relevance)
#     top_n_rank_list = [top_n_rank_list[i] + top_n_rank[i] for i in range(len(top_n_rank))]
#     return top_n_rank_list


def main():
    # set timer to measure Elapsed Time
    start_time = time.time()

    #initializing dataset
    dataset = DataSet()

    # Parsing documents
    dataset.create_document_space()

    # Printing to output the amount of documents in the document space
    print("JAVA FILES  = ", dataset.get_source_code_list_lenght())
    print("BUG REPORTS = ", dataset.get_bug_report_list_lenght())

    # Compute all bug reports
    bug_locator = BugLocalization(dataset)
    bug_locator.run()

    # Calculating and printing metrics printing metrics
    metric = Metrics(dataset)
    metric.calculate()
    print("---top_n_rank_list ---")
    print(dataset.files_pos_ranked)

    ranks_file.close()

    # Elapsed Time
    e = int(time.time() - start_time)
    print('\nElapsed Time: {:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))


if __name__ == "__main__":
    main()
