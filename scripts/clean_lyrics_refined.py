import json
import re
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    arties = json.load(f)

# Exact phrases and patterns from Webdunia article prose that are NOT holy verses
EXPLICIT_PROSE_PHRASES = [
    "श्री दुर्गा जी की आरती | Maa Durga ji ki Aarti",
    "माता दुर्गा के कई रूप हैं",
    "Ganpati vandana in hindi:",
    "मैं सिद्धिप्रदाता, अभीष्टदायी, पार्वतीनन्दन भगवान् गणेश की वन्दना करता हूं",
    "महाशिवरात्रि के दिन भगवान शिव जी की पूजा-आराधना",
    "khatu shyam baba ki aartiAarti shyam baba ki:",
    "2. खाटू श्याम आरती पाठ विधि",
    "एक छोटा सुझाव:",
    "उत्तर: खाटू श्याम जी",
    "उत्तर: महाभारत युद्ध",
    "उत्तर: बर्बरीक को",
    "उत्तर: निशान एक प्रकार",
    "दुर्गाष्टमी 2019 : इस दिन होता है महागौरी पूजन",
    "ALSO READ:",
    "एकादशी पर इस आरती से प्रसन्न होंगे श्री विष्णु",
    "अनुभवी लेखक, पत्रकार, संपादक",
    "Aarti of Karwa Chauth in Hindi:",
    "हिंदू माह कार्तिक मास के कृष्ण पक्ष की चतुर्थी को यह",
    "नवरात्रि के पहले दिन की जाती है मां शैलपुत्री की पूजा",
    "भगवान श्री गणेश की पूजा के बिना हिंदू धर्म में कोई भी पूजा पूरी नहीं मानी जाती",
    "अक्षय तृतीया पर भगवान परशुराम जी का जन्म हुआ था इसलिए",
    "Devi Matangi Stuti Aarti",
    "दस महाविद्याओं में से नौवीं महाविद्या देवी मातंगी",
    "Saraswati Mata Aarti : आज माता सरस्वती की जयंती",
    "Lakshmi Narayan Aarti: भगवान श्री लक्ष्मी नारायण जी की कई आरतियां प्रचलित हैं",
    "Dharamraj ji ki aarti: कार्तिक माह की कृष्ण चतुर्दशी",
    "दीपक जलाएं तथा सबसे पहले श्री गणेश की पूजा अर्चना",
    "इसके बाद ऋतु फल या पंचामृत या सुपारी का भोग लगाएं",
    "नवरात्रि में दुर्गा पूजा के दौरान अष्टमी के दिन मां दुर्गा के महागौरी रूप",
    "Krishna jee ki aarti : भगवान श्री कृष्ण के जन्मोत्सव पर पढ़ें",
    "संपादक और विषय-विशेषज्ञों द्वारा",
    "संदर्भ : आरती संग्रह गीता प्रेस गोरखपुर",
    "आरती: भगवान श्री कुबेर जी की Aarti Bhagwan Shri Kuber Ji",
    "Hartalika teej aarti: हरतालिका तीज की आरती",
    "Arti Shiv Ji Ki : आरती हर-हर महादेव जी की"
]

def is_unwanted(line, title_en, title_hi):
    l = line.strip()
    if not l:
        return True
        
    for p in EXPLICIT_PROSE_PHRASES:
        if p in l:
            return True
            
    # Check if line begins with English article prefix followed by colon
    if re.match(r'^[A-Za-z\s]+(Aarti|Chalisa|Stuti)\s*:', l):
        return True
        
    # Check if line is exact repeat of Aarti title
    if l == title_hi or l == title_en:
        return True

    # Check if line is FAQ or Q&A
    if l.startswith("उत्तर:") or l.startswith("प्रश्न:") or l.startswith("उत्तर :") or l.startswith("प्रश्न :"):
        return True

    # Standalone numbers
    if re.match(r'^\d+[\.\)\-]?$', l):
        return True

    # English title lines like "Vishnu Ji Ki Aarti" or "Ganesh Aarti"
    if re.match(r'^[A-Za-z\s]+(Ki Aarti|Aarti|Chalisa)$', l, re.I) and len(l) < 45:
        return True

    return False

cleaned_count = 0
sections_removed = 0

for a in arties:
    t_en = a.get('title', '')
    t_hi = a.get('title_devanagari', '')
    sections = a.get('lyrics_devanagari', [])
    
    new_sections = []
    seen_sigs = set()
    
    for sec in sections:
        sec_type = sec.get('type', 'verse')
        lines = sec.get('lines', [])
        
        good_lines = []
        for line in lines:
            if is_unwanted(line, t_en, t_hi):
                cleaned_count += 1
            else:
                good_lines.append(line.strip())
                
        if not good_lines:
            sections_removed += 1
            continue
            
        sig = ' || '.join(good_lines)
        if sig in seen_sigs:
            sections_removed += 1
            continue
        seen_sigs.add(sig)
        
        new_sections.append({
            'type': sec_type,
            'lines': good_lines
        })
        
    if new_sections:
        if not any(s['type'] == 'chorus' for s in new_sections):
            new_sections[0]['type'] = 'chorus'
            
    a['lyrics_devanagari'] = new_sections

print(f"Removed unwanted lines: {cleaned_count}")
print(f"Removed empty/duplicate sections: {sections_removed}")

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(arties, f, ensure_ascii=False, indent=2)

print("Saved cleanly to arties.json")
