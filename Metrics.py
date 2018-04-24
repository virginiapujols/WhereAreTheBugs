def mean_reciprocal_rank(rank_list, bug_report_size):
    sum_reciprocal_ranks = 0
    for i in rank_list:
        sum_reciprocal_ranks += 1 / i

    if sum_reciprocal_ranks < 0:
        sum_reciprocal_ranks *= -1

    mean_rank = sum_reciprocal_ranks / bug_report_size
    return mean_rank
