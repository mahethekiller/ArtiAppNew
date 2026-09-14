import sys, json

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('src/assets/data/arties.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

a = [x for x in data if x['id'] == 'arti-aarti-om-jai-jagdish-hare'][0]
print('ID:', a['id'])
print('Title:', a['title_devanagari'])
print('Total sections:', len(a['lyrics_devanagari']))
for idx, sec in enumerate(a['lyrics_devanagari']):
    print(f"Section {idx} ({sec['type']}):")
    for line in sec['lines']:
        print('   ', line)
