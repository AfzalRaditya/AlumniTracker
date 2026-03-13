import requests
from bs4 import BeautifulSoup
import urllib.parse

def scrape_alumni_data(name, campus):
    # --- TAHAP 1: COBA OPENALEX ---
    print(f"📡 Mencoba OpenAlex untuk: {name}...")
    oa_url = f"https://api.openalex.org/authors?search={name} {campus}"
    try:
        oa_res = requests.get(oa_url, timeout=5).json()
        if oa_res.get('results'):
            print("✅ Data ditemukan di OpenAlex!")
            return [{
                "name": r.get('display_name'),
                "org": r.get('last_known_institution', {}).get('display_name', campus),
                "link": r.get('id'),
                "bio": f"Akademisi - Works: {r.get('works_count')}"
            } for r in oa_res['results']]
    except:
        pass

    # --- TAHAP 2: FALLBACK KE GOOGLE (Untuk Alumni Umum/LinkedIn) ---
    print(f"🌐 OpenAlex NIHIL. Mencoba Google Search untuk: {name}...")
    query = f'"{name}" "{campus}"'
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        google_results = []
        
        # Mencari link hasil pencarian
        for g in soup.find_all('div', class_='tF2Cxc')[:3]: # Ambil 3 teratas
            google_results.append({
                "name": g.find('h3').text if g.find('h3') else name,
                "org": campus,
                "link": g.find('a')['href'],
                "bio": "Ditemukan via Web Search"
            })
        return google_results
    except Exception as e:
        print(f"❌ Scraper Error: {e}")
        return []