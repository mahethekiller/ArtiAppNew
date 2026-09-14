import os
import re
import json
import time
import sys
import shutil
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

RAW_HTML_PATH = r"C:\Users\user\.gemini\antigravity-ide\brain\07f270d5-6a56-4f0d-9809-b189b1ba6cfb\scratch\raw_aarti_list.html"
OUTPUT_ARTIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"
APP_IMAGES_DIR = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\public\assets\images\arties"
TOOLSITE_IMAGES_DIR = r"d:\SOFTWARES\xampp82new\htdocs\toolsite\public\images\arties"
CATEGORIES_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\categories.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'hi,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://hindi.webdunia.com/dharma/aarti'
}

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

def safe_url(url):
    try:
        parts = urllib.parse.urlsplit(url)
        path = urllib.parse.quote(parts.path)
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))
    except Exception:
        return url

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\r\t\xa0]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

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

def parse_aarti_page(url, fallback_title, fallback_img, slug_id):
    try:
        req_url = safe_url(url)
        r = requests.get(req_url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} for {url}")
            return None

        soup = BeautifulSoup(r.content.decode('utf-8', 'ignore'), 'html.parser')
        article = soup.find(class_=lambda c: c and 'article_in_content' in c)
        if not article:
            return None

        # 1. Title Extraction
        h1 = soup.find('h1')
        raw_h1 = clean_text(h1.get_text()) if h1 else fallback_title
        if not raw_h1:
            raw_h1 = fallback_title

        parts = raw_h1.split('|')
        title_dev = clean_text(parts[0])
        title_en = clean_text(parts[1]) if len(parts) > 1 else title_dev
        
        # Strip promotional labels from Hindi title
        title_dev = re.sub(r'^(दीपावली विशेष|शिवजी की आरती|वसंत पंचमी विशेष आरती|Navratri Aarti|Lord Ganesh Chalisa|Shri Ganesha aarti|Hartalika teej aarti|chhath ki aarti|dhanteras ki aarti|Arti Shiv Ji Ki|Aarti of Karwa Chauth in Hindi|Parshuram jayanti \d+|Janmashtami Aarti)\s*:\s*', '', title_dev)
        title_dev = re.sub(r'\s*:\s*(एकादशी पर|यहां पढ़ें|अति दुर्लभ|मंत्र-पुष्पांजलि|साहित|जानें).*$', '', title_dev).strip()

        # 2. Image Extraction & Direct Local Download
        image_src = ""
        img_tag = article.find('img', class_=lambda c: c and 'imgCont' in c) or article.find('img')
        if img_tag:
            srcset = img_tag.get('srcset', '')
            if srcset:
                # pick highest resolution from srcset (1200w)
                sources = [s.strip() for s in srcset.split(',') if s.strip()]
                for s in reversed(sources):
                    parts = s.split(' ')
                    if parts[0].startswith('http'):
                        image_src = parts[0]
                        break
            if not image_src:
                image_src = img_tag.get('src') or img_tag.get('data-src') or ""

        if not image_src or not image_src.startswith('http'):
            image_src = fallback_img

        local_img_rel = ""
        if image_src and image_src.startswith('http'):
            ext = '.jpg'
            local_filename = f"{slug_id}{ext}"
            app_local_path = os.path.join(APP_IMAGES_DIR, local_filename)
            toolsite_local_path = os.path.join(TOOLSITE_IMAGES_DIR, local_filename)
            
            if not os.path.exists(app_local_path) or os.path.getsize(app_local_path) == 0:
                try:
                    img_r = requests.get(image_src, headers=HEADERS, timeout=15)
                    if img_r.status_code == 200 and len(img_r.content) > 500:
                        with open(app_local_path, 'wb') as f:
                            f.write(img_r.content)
                        if os.path.exists(TOOLSITE_IMAGES_DIR):
                            shutil.copyfile(app_local_path, toolsite_local_path)
                except Exception as e:
                    print(f"  Image download error: {e}")
            else:
                # Ensure toolsite copy exists
                if os.path.exists(TOOLSITE_IMAGES_DIR) and not os.path.exists(toolsite_local_path):
                    shutil.copyfile(app_local_path, toolsite_local_path)

            local_img_rel = f"/assets/images/arties/{local_filename}"

        # 3. Intro / Significance Extraction (from text-align: justify)
        significance = ""
        intro_div = article.find(style=lambda s: s and 'text-align: justify' in s)
        if intro_div:
            intro_clone = BeautifulSoup(str(intro_div), 'html.parser')
            # Remove centered verse divs to only keep intro prose
            for c_div in intro_clone.find_all(style=lambda s: s and 'text-align: center' in s):
                c_div.decompose()
            raw_intro = intro_clone.get_text(separator=' ', strip=True)
            # Remove title prefix in intro
            clean_intro = re.sub(r'^[A-Za-z0-9\s\|\:\u0900-\u097F]+:\s*', '', raw_intro)
            if len(clean_intro) > 15:
                significance = clean_text(clean_intro)

        # 4. Pure Verse Extraction from text-align: center elements
        center_elements = article.find_all(style=lambda s: s and 'text-align: center' in s)
        stanzas = []
        current_lines = []

        for elem in center_elements:
            # Check if this element contains child center divs (avoid parent double-match)
            if elem.find(style=lambda s: s and 'text-align: center' in s):
                continue

            txt = clean_text(elem.get_text())
            
            # Stanza separator check
            if not txt or txt == '&nbsp;' or txt == 'nbsp':
                if current_lines:
                    stanzas.append(current_lines)
                    current_lines = []
                continue

            # Skip title repeats or labels inside verse block
            if (title_dev and title_dev in txt) or (title_en and title_en in txt) or ('Aarti' in txt and len(txt) < 35):
                continue
            if txt.startswith('श्री ') and 'आरती' in txt and len(txt) < 35:
                continue

            # Skip editorial intro / FAQ lines if any slipped in
            if any(bad in txt for bad in ['ALSO READ', 'अनुभवी लेखक', 'संपादक', 'Disclaimer', 'अस्वीकरण', 'उत्तर:', 'प्रश्न:']):
                continue

            current_lines.append(txt)

        if current_lines:
            stanzas.append(current_lines)

        # 5. Fallback if page did not use text-align: center
        if not stanzas:
            # Fallback: scan paragraphs with poetic punctuation
            for p in article.find_all(['p', 'div']):
                # Skip container if it has children
                if p.find(['p', 'div']):
                    continue
                txt = clean_text(p.get_text())
                if ('॥' in txt or '।' in txt or 'टेक' in txt) and not any(bad in txt for bad in ['ALSO READ', 'संपादक', 'Disclaimer']):
                    lines = [clean_text(l) for l in txt.split('\n') if clean_text(l)]
                    if lines:
                        stanzas.append(lines)

        # Format into structured chorus + verse sections
        lyrics_sections = []
        for idx, st in enumerate(stanzas):
            is_chorus = (idx == 0) or any('टेक' in l or '॥ टेक' in l for l in st)
            lyrics_sections.append({
                'type': 'chorus' if is_chorus else 'verse',
                'lines': st
            })

        if not lyrics_sections:
            return None

        # Category detection
        cat_id = detect_category(title_dev, significance)
        deity_en, deity_hi = DEITY_INFO.get(cat_id, ('Devi Devta', 'देवी-देवता'))

        return {
            "id": slug_id,
            "category_id": cat_id,
            "title": title_en,
            "title_devanagari": title_dev,
            "deity": deity_en,
            "deity_devanagari": deity_hi,
            "popular": False,
            "timing": "Daily Pooja / Aarti",
            "timing_devanagari": "नित्य पूजन एवं आरती",
            "duration_minutes": 4,
            "significance": significance or f"{deity_hi} की पावन एवं मंगलकारी आरती।",
            "significance_devanagari": significance or f"{deity_hi} की पावन एवं मंगलकारी आरती।",
            "image": local_img_rel,
            "lyrics_devanagari": lyrics_sections
        }

    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        return None

def main():
    os.makedirs(APP_IMAGES_DIR, exist_ok=True)
    os.makedirs(TOOLSITE_IMAGES_DIR, exist_ok=True)

    with open(RAW_HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = soup.find_all('aside', class_='db_arti_block')

    seen_urls = set()
    extracted_items = []

    for block in blocks:
        a_tag = block.find('a', href=True)
        if not a_tag:
            continue
        rel_href = a_tag['href']
        full_url = rel_href if rel_href.startswith('http') else ('https://hindi.webdunia.com' + rel_href)
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)

        img_tag = block.find('img')
        fallback_img = img_tag.get('src') if img_tag else ""
        fallback_title = (img_tag.get('alt') or img_tag.get('title') or "").strip() if img_tag else ""
        h3 = block.find('h3')
        if h3 and h3.get_text(strip=True):
            fallback_title = h3.get_text(strip=True)

        slug_match = re.search(r'/([^/]+)-\d+_\d+\.html', full_url)
        slug_id = f"arti-{slug_match.group(1)}" if slug_match else f"arti-{len(extracted_items)+1}"

        extracted_items.append({
            'url': full_url,
            'title': fallback_title,
            'thumbnail': fallback_img,
            'slug_id': slug_id
        })

    print(f"Total unique Aartis to scrape with precise V2 pipeline: {len(extracted_items)}")

    scraped_arties = []
    for i, item in enumerate(extracted_items, 1):
        print(f"[{i}/{len(extracted_items)}] Scraping: {item['slug_id']} ...")
        res = parse_aarti_page(item['url'], item['title'], item['thumbnail'], item['slug_id'])
        if res and res.get('lyrics_devanagari'):
            scraped_arties.append(res)
        time.sleep(0.3)

    print(f"\nSuccessfully scraped {len(scraped_arties)} clean Aartis from Webdunia.")

    # Load baseline curated Aartis (first 12 baseline non-scraped items)
    with open(OUTPUT_ARTIES_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    curated_baseline = [a for a in existing if not a['id'].startswith('arti-') and not a['id'].startswith('wd-')]
    print(f"Curated baseline Aartis: {len(curated_baseline)}")

    final_merged = list(curated_baseline)
    seen_ids = {a['id'] for a in curated_baseline}

    for item in scraped_arties:
        if item['id'] not in seen_ids:
            final_merged.append(item)
            seen_ids.add(item['id'])

    print(f"Total consolidated Aartis: {len(final_merged)}")

    # Save to arties.json
    with open(OUTPUT_ARTIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_merged, f, ensure_ascii=False, indent=2)
    print(f"Saved cleanly to {OUTPUT_ARTIES_PATH}")

    # Update categories counts
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    cat_counts = {}
    for a in final_merged:
        c = a.get('category_id', 'special')
        cat_counts[c] = cat_counts.get(c, 0) + 1

    for cat in categories:
        cat['arti_count'] = cat_counts.get(cat['id'], 0)

    with open(CATEGORIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    print("\nUpdated category counts:")
    for cat in categories:
        print(f"  - {cat['name_devanagari']} ({cat['id']}): {cat['arti_count']}")

if __name__ == '__main__':
    main()
