import json
from prettytable import PrettyTable

def print_stats():
    with open('data/links/master_link.json', 'r', encoding='utf-8') as f:
        master = json.load(f)

    table = PrettyTable()
    table.field_names = [
        "Book ID", 
        "Total Anchor", 
        "AR + EN + ID (Lidwa & AB)", 
        "AR + ID (Lidwa Only)", 
        "AR + EN (AB Only)", 
        "AR Only (Unlinked)"
    ]

    # Align left for Book ID, right for numbers
    table.align["Book ID"] = "l"
    for field in table.field_names[1:]:
        table.align[field] = "r"

    total_anchor_all = 0
    total_both_all = 0
    total_lidwa_only_all = 0
    total_ab_only_all = 0
    total_unlinked_all = 0

    for book, hadiths in master.items():
        total_anchor = len(hadiths)
        
        both = sum(1 for h in hadiths.values() if h.get('lidwa_id') and h.get('ahmedbaset_id'))
        lidwa_only = sum(1 for h in hadiths.values() if h.get('lidwa_id') and not h.get('ahmedbaset_id'))
        ab_only = sum(1 for h in hadiths.values() if not h.get('lidwa_id') and h.get('ahmedbaset_id'))
        unlinked = sum(1 for h in hadiths.values() if not h.get('lidwa_id') and not h.get('ahmedbaset_id'))

        total_anchor_all += total_anchor
        total_both_all += both
        total_lidwa_only_all += lidwa_only
        total_ab_only_all += ab_only
        total_unlinked_all += unlinked

        table.add_row([
            book,
            f"{total_anchor:,}",
            f"{both:,}",
            f"{lidwa_only:,}",
            f"{ab_only:,}",
            f"{unlinked:,}"
        ])

    # Add total row
    table.add_row([
        "TOTAL",
        f"{total_anchor_all:,}",
        f"{total_both_all:,}",
        f"{total_lidwa_only_all:,}",
        f"{total_ab_only_all:,}",
        f"{total_unlinked_all:,}"
    ])

    print(table)

if __name__ == "__main__":
    print_stats()
