import json
import re
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    arties = json.load(f)

print(f"Total Aartis to clean: {len(arties)}")

# Common introductory news lead-in phrases to remove from verses
INTRO_PHRASES = [
    "यह आरती करने से",
    "यहां पढ़ें",
    "पाठकों के लिए प्रस्तुत",
    "प्रसन्न होकर खुशहाल जीवन",
    "आशीर्वाद देते हैं",
    "कृपा बरसाते हैं",
    "का खास त्योहार है",
    "की पूजा के बिना",
    "अक्षय तृतीया पर",
    "दस महाविद्याओं में",
    "आज माता सरस्वती",
    "भगवान श्री लक्ष्मी नारायण जी की कई आरतियां",
    "कार्तिक माह की",
    "दीपक जलाएं तथा",
    "इसके बाद ऋतु फल",
    "नवरात्रि में दुर्गा पूजा के दौरान",
    "भगवान श्री कृष्ण के जन्मोत्सव पर पढ़ें",
    "संदर्भ : आरती संग्रह",
    "Hartalika teej aarti:",
    "Arti Shiv Ji Ki :",
    "श्री विष्णु की आरती :",
    "श्री दुर्गा जी की आरती |",
    "Ganpati vandana in hindi:",
    "Aarti of Karwa Chauth in Hindi:",
    "Saraswati Mata Aarti :",
    "Lakshmi Narayan Aarti:",
    "Dharamraj ji ki aarti:",
    "Krishna jee ki aarti :",
    "Aarti Shri Parashuram Ji Ki :",
    "Devi Matangi Stuti Aarti",
    "जो भी भक्त सच्चे मन से बाबा का ध्यान करता है",
    "मैं सिद्धिप्रदाता, अभीष्टदायी, पार्वतीनन्दन"
]

def clean_title(title):
    # e.g. "Om Jai Jagdish Hare Aarti : एकादशी पर इस आरती से प्रसन्न होंगे श्री विष्णु" -> "ॐ जय जगदीश हरे आरती"
    t = title
    if "Om Jai Jagdish Hare" in t:
        return "ॐ जय जगदीश हरे आरती"
    if "Hartalika teej" in t:
        return "हरतालिका तीज की आरती"
    if "dhanteras ki aarti" in t:
        return "भगवान धन्वन्तरि की आरती"
    if "chhath ki aarti" in t:
        return "छठ मैया की आरती"
    if "Arti Shiv Ji Ki" in t:
        return "आरती हर-हर महादेव जी की"
    if "Aarti of Karwa Chauth" in t or "करवा चौथ की आरती" in t:
        return "करवा चौथ की आरती"
    if "Parshuram" in t:
        return "भगवान परशुराम जी की आरती"
    if "Janmashtami Aarti" in t:
        return "भगवान श्री कृष्ण की आरती"
        
    # Remove English prefixes if Devanagari follows
    t = re.sub(r'^[A-Za-z0-9\s\-_]+:\s*', '', t)
    # Remove promotional trailers like " : यहां पढ़ें एक साथ" or " : एकादशी पर..."
    t = re.sub(r'\s*:\s*(एकादशी पर|यहां पढ़ें|अति दुर्लभ|मंत्र-पुष्पांजलि|साहित|जानें).*$', '', t)
    return t.strip()

for a in arties:
    # 1. Clean title
    old_title = a.get('title_devanagari', '')
    a['title_devanagari'] = clean_title(old_title)
    
    # 2. Clean lines inside sections
    raw_sections = a.get('lyrics_devanagari', [])
    valid_sections = []
    
    for sec in raw_sections:
        clean_lines = []
        for line in sec.get('lines', []):
            l = line.strip()
            if not l:
                continue
            # Check intro phrases
            if any(p in l for p in INTRO_PHRASES):
                continue
            # Check if line is just a title or label
            if l in [a.get('title'), old_title, a['title_devanagari']]:
                continue
            if re.match(r'^[A-Za-z\s]+(Aarti|Chalisa)$', l, re.I):
                continue
            clean_lines.append(l)
            
        if clean_lines:
            valid_sections.append({
                'type': sec.get('type', 'verse'),
                'lines': clean_lines
            })

    # 3. Detect and remove subset fragments:
    # If the first section contains 8+ lines (a full hymn) and subsequent sections
    # are single lines that all already exist in the first section, drop the redundant fragments!
    if len(valid_sections) > 1 and len(valid_sections[0]['lines']) >= 6:
        first_sec_lines = set(valid_sections[0]['lines'])
        filtered_sections = [valid_sections[0]]
        
        is_fragmented = True
        for s in valid_sections[1:]:
            # If section has only 1 or 2 lines and all exist in first_sec_lines, it's a fragment
            if len(s['lines']) <= 2 and all(l in first_sec_lines for l in s['lines']):
                continue
            else:
                is_fragmented = False
                filtered_sections.append(s)
                
        if len(filtered_sections) < len(valid_sections):
            valid_sections = filtered_sections

    # 4. If an Aarti only has one giant section with 12+ lines, split it into chorus + verses for better reading experience
    if len(valid_sections) == 1 and len(valid_sections[0]['lines']) >= 8:
        all_lines = valid_sections[0]['lines']
        split_sections = []
        # First 2 lines or first chorus
        split_sections.append({'type': 'chorus', 'lines': all_lines[:2]})
        # Subsequent verses in blocks of 2 to 4 lines
        idx = 2
        while idx < len(all_lines):
            block = all_lines[idx:idx+2]
            split_sections.append({'type': 'verse', 'lines': block})
            idx += 2
        valid_sections = split_sections
    elif valid_sections:
        valid_sections[0]['type'] = 'chorus'

    a['lyrics_devanagari'] = valid_sections

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(arties, f, ensure_ascii=False, indent=2)

print(f"Master cleaning completed for {len(arties)} Aartis.")
