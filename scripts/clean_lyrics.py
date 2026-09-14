import json
import re
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    arties = json.load(f)

print(f"Total Aartis before cleaning: {len(arties)}")

def is_noise_line(line, title_en, title_hi):
    l = line.strip()
    if not l:
        return True
    
    # 1. Obvious advertisement & promo prefixes
    l_lower = l.lower()
    bad_prefixes = [
        'also read', 'read also', 'यह भी पढ़ें', 'यह भी पढ़ें', 'यह भी देखें',
        'प्रश्न:', 'उत्तर:', 'q:', 'a:', 'नोट:', 'note:', 'नोट :', 'ध्यान दें',
        'संदर्भ:', 'संदर्भ :', 'साभार:', 'साभार :', 'फोटो साभार', 'स्रोत:',
        'अस्वीकरण', 'disclaimer', 'कॉपीराइट', 'copyright', 'उत्तर :', 'प्रश्न :'
    ]
    for bp in bad_prefixes:
        if l_lower.startswith(bp) or l.startswith(bp):
            return True

    # 2. Boilerplate / disclaimers anywhere in line
    bad_contains = [
        'ALSO READ', 'अनुभवी लेखक', 'पत्रकार, संपादक', 'विचारोत्तेजक आलेखों',
        'वेबदुनिया', 'Webdunia', 'कॉपीराइट', 'सर्वाधिकार सुरक्षित',
        'अस्वीकरण', 'Disclaimer', 'धार्मिक मान्यताएं', 'इंटरनेट पर मौजूद',
        'क्लिक करें', 'शेयर करें', 'WhatsApp', 'Facebook',
        'आरती पाठ विधि', 'खाटू श्याम आरती पाठ विधि', 'स्थापना के मंत्र',
        'एक छोटा सुझाव:'
    ]
    for bc in bad_contains:
        if bc in l:
            return True

    # 3. Exact matches of title or English romanized title label
    if l in [title_en, title_hi]:
        return True
    if re.match(r'^[A-Za-z\s]+(Ki Aarti|ki aarti|Aarti|Chalisa)$', l, re.I):
        return True

    # 4. Standalone numbers, bullets or roman numerals
    if re.match(r'^\d+[\.\)\-]?$', l):
        return True
    if re.match(r'^[ivxIVX]+[\.\)]?$', l):
        return True

    # 5. Explanatory intro/outro sentences that are clearly journalistic prose, not poetry
    prose_markers = [
        'यहां पढ़ें', 'यहां प्रस्तुत है', 'पाठकों के लिए प्रस्तुत', 'प्रसन्न होकर खुशहाल जीवन',
        'आशीर्वाद देते हैं।', 'कृपा बरसाते हैं।', 'का खास त्योहार है।', 'की जाती है मां',
        'का गायन करना हृदय को', 'कहा जाता है कि', 'आरती के पूर्व भी इसे पढ़ा'
    ]
    if any(pm in l for pm in prose_markers) and not ('॥' in l or 'जय' in l or 'ॐ' in l):
        return True

    # 6. FAQ answers (e.g. "उत्तर: खाटू श्याम जी महाभारत काल...")
    if l.startswith('उत्तर') or l.startswith('प्रश्न'):
        return True

    return False

total_removed_lines = 0
total_removed_sections = 0

for a in arties:
    title_en = a.get('title', '')
    title_hi = a.get('title_devanagari', '')
    raw_sections = a.get('lyrics_devanagari', [])
    
    cleaned_sections = []
    seen_section_signatures = set()
    
    for sec in raw_sections:
        sec_type = sec.get('type', 'verse')
        lines = sec.get('lines', [])
        
        valid_lines = []
        for line in lines:
            if not is_noise_line(line, title_en, title_hi):
                valid_lines.append(line.strip())
            else:
                total_removed_lines += 1
                
        if not valid_lines:
            total_removed_sections += 1
            continue
            
        # Deduplicate identical consecutive or repeating sections
        sig = ' || '.join(valid_lines)
        if sig in seen_section_signatures:
            total_removed_sections += 1
            continue
        seen_section_signatures.add(sig)
        
        cleaned_sections.append({
            'type': sec_type,
            'lines': valid_lines
        })
        
    # Ensure first section is marked chorus if not already
    if cleaned_sections:
        if not any(s['type'] == 'chorus' for s in cleaned_sections):
            cleaned_sections[0]['type'] = 'chorus'
            
    a['lyrics_devanagari'] = cleaned_sections

print(f"Total noise lines removed: {total_removed_lines}")
print(f"Total duplicate/empty sections removed: {total_removed_sections}")

# Write back to arties.json
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(arties, f, ensure_ascii=False, indent=2)

print(f"Successfully cleaned and saved {JSON_PATH}")
