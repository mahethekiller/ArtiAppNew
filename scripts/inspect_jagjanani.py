import json

with open('src/assets/data/arties.json', 'r', encoding='utf-8') as f:
    arties = json.load(f)

a = [x for x in arties if x['id'] == 'arti-maa-durga-ji-ki-aarti-in-hindi'][0]
with open('sample_jagjanani.txt', 'w', encoding='utf-8') as out:
    out.write('ID: ' + a['id'] + '\n')
    out.write('Title (Dev): ' + a['title_devanagari'] + '\n')
    out.write('Title (Eng): ' + a['title'] + '\n')
    out.write('Significance: ' + a['significance'] + '\n')
    out.write('Image: ' + a['image'] + '\n')
    out.write(f"Stanzas count: {len(a['lyrics_devanagari'])}\n\n")
    for i, s in enumerate(a['lyrics_devanagari']):
        out.write(f"Stanza {i} ({s['type']}):\n")
        for l in s['lines']:
            out.write('  ' + l + '\n')
        out.write('\n')

print("Wrote sample_jagjanani.txt")
