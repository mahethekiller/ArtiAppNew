import json
import re
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('src/assets/data/arties.json', 'r', encoding='utf-8') as f:
    arties = json.load(f)

print(f"Total Aartis in dataset: {len(arties)}")

# Patterns for unwanted noise
noise_keywords = [
    'disclaimer', 'अस्वीकरण', 'वेबदुनिया', 'webdunia', 'कॉपीराइट', 'copyright',
    'यह भी पढ़ें', 'यह भी देखें', 'यह भी पढ़ें', 'क्लिक करें', 'share', 'whatsapp', 'facebook',
    'संपादक', 'सम्पादक', 'रिपोर्ट', 'फोटो', 'साभार', 'स्रोत', 'source',
    'आरती करने के लाभ', 'आरती का महत्व', 'पूजा विधि', 'शुभ मुहूर्त', 'तिथि',
    'पाठ विधि', 'ध्यान दें', 'नोट:', 'note:', 'उपाय', 'टिप्स', 'विशेष महत्व',
    'कथा अनुसार', 'पौराणिक कथा', 'मान्यतानुसार', 'आइए पढ़ते हैं', 'प्रस्तुत है',
    'आइए जानते हैं', 'आरती के बोल', 'आरती संग्रह'
]

audit_results = []

for a in arties:
    a_id = a.get('id')
    title = a.get('title_devanagari', '')
    lyrics = a.get('lyrics_devanagari', [])
    
    noisy_lines = []
    
    for s_idx, sec in enumerate(lyrics):
        for l_idx, line in enumerate(sec.get('lines', [])):
            clean = line.strip()
            # 1. Check for noisy keywords
            matched_kw = [kw for kw in noise_keywords if kw in clean.lower()]
            if matched_kw:
                noisy_lines.append((s_idx, l_idx, matched_kw[0], clean))
            # 2. Check for long narrative prose (> 120 chars) that is clearly article explanation, not verses
            elif len(clean) > 120 and any(w in clean for w in ['भगवान', 'माता', 'पूजा', 'दिन', 'वर्ष', 'कहा जाता', 'मान्यता', 'भक्त']):
                noisy_lines.append((s_idx, l_idx, 'LONG_EXPLANATORY_PROSE', clean))
            # 3. Check for standalone numbers or symbols
            elif re.match(r'^\d+[\.\)]?$', clean):
                noisy_lines.append((s_idx, l_idx, 'STANDALONE_NUMBER', clean))
            # 4. Check for header-like repeats
            elif clean == title or clean == a.get('title'):
                noisy_lines.append((s_idx, l_idx, 'REPEATED_TITLE', clean))

    if noisy_lines:
        audit_results.append({
            'id': a_id,
            'title': title,
            'count': len(noisy_lines),
            'samples': noisy_lines
        })

print(f"\nAartis with suspected unwanted lines: {len(audit_results)}")

with open('scratch_audit_report.txt', 'w', encoding='utf-8') as out:
    for res in audit_results:
        out.write(f"\n=========================================\n")
        out.write(f"[{res['id']}] {res['title']} (Found: {res['count']})\n")
        for s_idx, l_idx, kw, line in res['samples']:
            out.write(f"  - [{kw}] (sec {s_idx}, line {l_idx}): {line[:120]}\n")

print("Detailed report written to scratch_audit_report.txt")
