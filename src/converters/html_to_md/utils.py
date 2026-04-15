from itertools import groupby


def gather_by_domain(blocks):
    runs = []

    for domain, group in groupby(blocks, key=lambda b: b.domain):
        runs.append((domain, list(group)))

    return runs
