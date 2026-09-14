import json
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARTIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"
CATEGORIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\categories.json"

def remove_dummies():
    with open(ARTIES_PATH, 'r', encoding='utf-8') as f:
        arties = json.load(f)

    dummy_arties = [a for a in arties if not a['id'].startswith('arti-')]
    real_arties = [a for a in arties if a['id'].startswith('arti-')]

    print(f"Total aartis before: {len(arties)}")
    print(f"Dummy aartis to remove: {len(dummy_arties)}")
    for d in dummy_arties:
        print(f"  - Removing dummy: {d['id']} ({d.get('title')})")

    print(f"Retaining {len(real_arties)} genuine extracted aartis.")

    # Save cleaned arties.json
    with open(ARTIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(real_arties, f, ensure_ascii=False, indent=2)

    # Update categories
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    counts = {}
    for a in real_arties:
        c = a.get('category_id', 'special')
        counts[c] = counts.get(c, 0) + 1

    active_categories = []
    for c in categories:
        cid = c['id']
        cnt = counts.get(cid, 0)
        if cnt > 0:
            c['arti_count'] = cnt
            active_categories.append(c)
            print(f"  + Category {cid} ({c['name_devanagari']}): {cnt} aartis")
        else:
            print(f"  - Dropping empty category: {cid} ({c.get('name')})")

    with open(CATEGORIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(active_categories, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(active_categories)} categories with accurate counts.")

if __name__ == '__main__':
    remove_dummies()
