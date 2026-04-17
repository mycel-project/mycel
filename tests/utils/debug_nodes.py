import datetime

def ms_to_str(ms):
    if ms is None:
        return "None"
    return datetime.datetime.fromtimestamp(ms / 1000).strftime("%y/%m/%d %H:%M")


def short_id(_id):
    s = str(_id)
    return s[-8:]


def format_overdue(due_ms, now_ms):
    if due_ms is None:
        return "None"

    diff = now_ms - due_ms

    if diff <= 0:
        return "0"

    minutes = diff // (60_000)
    hours = diff // (3_600_000)
    days = diff // (86_400_000)

    if days > 0:
        return f"{days}d"
    if hours > 0:
        return f"{hours}h"
    return f"{minutes}m"

def print_nodes(nodes):
    print()

    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)

    index_by_id = {n.id: i for i, n in enumerate(nodes)}

    children = {n.id: [] for n in nodes}
    roots = []

    for n in nodes:
        if n.parent_id is None:
            roots.append(n)
        else:
            children.setdefault(n.parent_id, []).append(n)

    rows = []

    def walk(n, depth=0):
        rows.append({
            "tree": "  " * depth + "└─",
            "pos": index_by_id[n.id],
            "id": short_id(n.id),
            "prio": n.priority,
            "due": ms_to_str(n.due),
            "last_review": ms_to_str(n.last_review),
            "overdue": format_overdue(n.due, now),
        })

        for c in children.get(n.id, []):
            walk(c, depth + 1)

    for r in roots:
        walk(r)

    headers = ["tree", "pos", "id", "prio", "due", "last_review", "overdue"]

    col_widths = {
        h: max(len(h), max(len(str(r[h])) for r in rows)) if rows else len(h)
        for h in headers
    }

    def fmt_row(r):
        return " | ".join(str(r[h]).ljust(col_widths[h]) for h in headers)

    header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
    sep = "-+-".join("-" * col_widths[h] for h in headers)

    print(header_line)
    print(sep)

    for r in rows:
        print(fmt_row(r))
