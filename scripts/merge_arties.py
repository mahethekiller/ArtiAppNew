import json
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

EXISTING_ARTIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"
EXTRACTED_ARTIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties_extracted.json"
CATEGORIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\categories.json"

def merge():
    if not os.path.exists(EXTRACTED_ARTIES_PATH):
        print(f"Extracted arties not found at {EXTRACTED_ARTIES_PATH}")
        return

    with open(EXISTING_ARTIES_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    with open(EXTRACTED_ARTIES_PATH, 'r', encoding='utf-8') as f:
        extracted = json.load(f)

    print(f"Existing Aartis count: {len(existing)}")
    print(f"Extracted Aartis count: {len(extracted)}")

    # Collect existing titles to avoid exact duplicates
    existing_titles = set()
    for a in existing:
        t = a.get('title_devanagari', '').replace(' ', '').replace(':', '').replace('-', '')
        existing_titles.add(t)

    # Curated baseline are the items not starting with 'wd-'
    curated_baseline = [a for a in existing if not a['id'].startswith('wd-')]
    print(f"Curated baseline Aartis: {len(curated_baseline)}")
    
    merged = list(curated_baseline)
    seen_ids = {a['id'] for a in curated_baseline}
    
    for item in extracted:
        if item['id'] not in seen_ids:
            merged.append(item)
            seen_ids.add(item['id'])

    with open(EXISTING_ARTIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Total merged Aartis: {len(merged)} saved to {EXISTING_ARTIES_PATH}")

    # Update category counts
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    cat_counts = {}
    for a in merged:
        c = a.get('category_id', 'special')
        cat_counts[c] = cat_counts.get(c, 0) + 1

    for cat in categories:
        cat['arti_count'] = cat_counts.get(cat['id'], 0)

    with open(CATEGORIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    print("Updated categories.json with accurate aarti counts:")
    for cat in categories:
        print(f"  - {cat['name_devanagari']} ({cat['id']}): {cat['arti_count']}")

if __name__ == '__main__':
    merge()
