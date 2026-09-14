import json
import re
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAW_JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\webdunia_arties_raw.json"
OUTPUT_ARTIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties_extracted.json"

CATEGORY_MAP = [
    ('kuber', ['कुबेर', 'kuber']),
    ('ganga', ['गंगा मैया', 'गंगा आरती', 'गंगा', 'ganga']),
    ('shyam', ['खाटू श्याम', 'श्याम', 'khatu']),
    ('saraswati', ['सरस्वती', 'शारदा', 'saraswati']),
    ('surya', ['सूर्य', 'surya', 'भास्कर']),
    ('ganesh', ['गणेश', 'गणपति', 'विनायक', 'गजानन', 'लम्बोदर', 'ganesh', 'ganpati']),
    ('hanuman', ['हनुमान', 'बजरंगबली', 'मारुति', 'पवनसुत', 'विचित्रवीर', 'hanuman']),
    ('durga', ['दुर्गा', 'अम्बे', 'काली', 'शैलपुत्री', 'ब्रह्मचारिणी', 'चंद्रघंटा', 'कूष्मांडा', 'स्कंद', 'कात्यायनी', 'कालरात्रि', 'महागौरी', 'सिद्धिदात्री', 'जगजननी', 'नवरात्रि', 'पार्वती', 'durga', 'navratri', 'ambe']),
    ('krishna', ['कृष्ण', 'कान्हा', 'गोविन्द', 'गोपाल', 'जन्माष्टमी', 'krishna']),
    ('lakshmi', ['महालक्ष्मी', 'लक्ष्मी', 'धनतेरस', 'दीपावली', 'lakshmi', 'laxmi']),
    ('vishnu', ['विष्णु', 'सत्यनारायण', 'जगदीश', 'नारायण', 'लक्ष्मीनारायण', 'नरसिंह', 'vishnu', 'jagdish']),
    ('shiva', ['शिव', 'भोलेनाथ', 'महादेव', 'शंकर', 'रुद्र', 'गंगाधर', 'shiva', 'shiv']),
    ('special', ['तुलसी', 'गौमाता', 'गाय', 'करवा चौथ', 'छठ', 'हरतालिका', 'परशुराम', 'महावीर', 'चित्रगुप्त', 'यमराज', 'धन्वंतरि', 'ब्रह्मा'])
]

DEITY_INFO = {
    'ganesh': ('Lord Ganesha', 'श्री गणेश जी'),
    'shiva': ('Lord Shiva', 'भगवान शिव'),
    'durga': ('Maa Durga', 'मां दुर्गा'),
    'hanuman': ('Lord Hanuman', 'श्री हनुमान जी'),
    'krishna': ('Lord Krishna', 'भगवान श्री कृष्ण'),
    'vishnu': ('Lord Vishnu', 'भगवान श्री विष्णु'),
    'lakshmi': ('Maa Lakshmi', 'मां महालक्ष्मी'),
    'kuber': ('Lord Kuber', 'भगवान श्री कुबेर'),
    'saraswati': ('Maa Saraswati', 'मां सरस्वती'),
    'ganga': ('Maa Ganga', 'मां गंगा मैया'),
    'surya': ('Surya Dev', 'भगवान सूर्य देव'),
    'shyam': ('Khatu Shyam Baba', 'बाबा खाटू श्याम'),
    'special': ('Devi Devta', 'देवी-देवता')
}

def detect_category(title, text):
    title_lower = title.lower()
    for cat_id, keywords in CATEGORY_MAP:
        for kw in keywords:
            if kw.lower() in title_lower:
                return cat_id
    search_str = (title + ' ' + text).lower()
    for cat_id, keywords in CATEGORY_MAP:
        for kw in keywords:
            if kw.lower() in search_str:
                return cat_id
    return 'special'

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)[:50]

def clean_title(raw_title):
    # e.g., "गणेश आरती, सुखकर्ता दुखहर्ता वार्ता विघ्नाची जयदेव जयदेव | Ganesh Aarti..."
    parts = raw_title.split('|')
    hindi_part = parts[0].strip()
    english_part = parts[1].strip() if len(parts) > 1 else ""
    
    # clean colon prefixes like "दीपावली विशेष : "
    hindi_part = re.sub(r'^(दीपावली विशेष|शिवजी की आरती|वसंत पंचमी विशेष आरती|Navratri Aarti|Lord Ganesh Chalisa|Shri Ganesha aarti)\s*:\s*', '', hindi_part)
    return hindi_part.strip(), english_part.strip()

def process_lyrics(paragraphs):
    verses = []
    current_lines = []
    
    for para in paragraphs:
        # Ignore obvious introductory / outro metadata paragraphs
        if any(bad in para for bad in ['आरती का महत्व', 'पूजा विधि', 'शुभ मुहूर्त', 'लाभ', 'ध्यान दें', 'संबंधित आलेख']):
            continue
        
        lines = [l.strip() for l in para.split('\n') if l.strip()]
        if not lines:
            continue
            
        # Is this paragraph part of the hymn/aarti?
        # Check if lines have poetic or devotional cadence (॥, ।, जय, ॐ, etc.)
        verse_lines = []
        for line in lines:
            # Skip advertisement or author lines
            if len(line) < 3 or 'क्लिक करें' in line or 'शेयर करें' in line:
                continue
            verse_lines.append(line)
            
        if verse_lines:
            verses.append({
                "type": "chorus" if len(verses) == 0 else "verse",
                "lines": verse_lines
            })
            
    return verses

def process_file():
    if not os.path.exists(RAW_JSON_PATH):
        print(f"File not found: {RAW_JSON_PATH}")
        return
        
    with open(RAW_JSON_PATH, 'r', encoding='utf-8') as f:
        items = json.load(f)
        
    arties = []
    for idx, item in enumerate(items, 1):
        url = item.get('url', '')
        raw_title = item.get('title', '')
        image = item.get('image', '')
        paras = item.get('paragraphs', [])
        
        hindi_title, eng_title = clean_title(raw_title)
        if not hindi_title:
            hindi_title = raw_title
        if not eng_title:
            eng_title = hindi_title
            
        full_text = ' '.join(paras[:5])
        cat_id = detect_category(raw_title, full_text)
        deity_en, deity_hi = DEITY_INFO.get(cat_id, ('Devi Devta', 'देवी-देवता'))
        
        slug_match = re.search(r'/([^/]+)-\d+_\d+\.html', url)
        slug_id = slug_match.group(1) if slug_match else f"aarti-{idx}"
        
        lyrics = process_lyrics(paras)
        if not lyrics:
            # Fallback if no verses detected
            lyrics = [{"type": "verse", "lines": [p for p in paras if len(p) > 10][:8]}]
            
        arties.append({
            "id": f"wd-{slug_id}",
            "category_id": cat_id,
            "title": eng_title,
            "title_devanagari": hindi_title,
            "deity": deity_en,
            "deity_devanagari": deity_hi,
            "popular": idx <= 10,
            "timing": "Daily Pooja / Aarti",
            "timing_devanagari": "नित्य पूजन एवं आरती",
            "duration_minutes": 4,
            "significance": f"Sacred Aarti of {deity_en} from Webdunia collection.",
            "significance_devanagari": f"{deity_hi} की पावन एवं मंगलकारी आरती।",
            "image": image,
            "webdunia_url": url,
            "lyrics_devanagari": lyrics
        })
        
    with open(OUTPUT_ARTIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(arties, f, ensure_ascii=False, indent=2)
        
    print(f"Processed {len(arties)} Aartis successfully saved to {OUTPUT_ARTIES_PATH}")

if __name__ == '__main__':
    process_file()
