import math


def get_page_count(item_count, page_size):
    return max(math.ceil(item_count / page_size), 1)
