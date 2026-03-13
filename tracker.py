import os
import re
import time
from supabase import create_client
from dotenv import load_dotenv
from scraper_engine import scrape_alumni_data

# --- KONFIGURASI ---
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# --- LOGIKA REFERENSI (ADOPTI DARI PROTOTIPE JS) ---

def tokenize(text):
    """Lowercase, hapus simbol, minimal 2 karakter (Persis logic JS)"""
    if not text: return []
    clean = re.sub(r'[^a-z0-9\s.-]', '', text.lower())
    return [t for t in clean.split() if len(t) >= 2]

def score_evidence(profile, candidate):
    """
    Menghitung skor berdasarkan hits token (Nama: 18, Prodi: 8, Kampus: 8).
    Mengadopsi fungsi scoreEvidence dari kode referensi Afzal.
    """
    name_tokens = tokenize(profile['name'])
    program_tokens = tokenize(profile.get('major', ''))
    campus_tokens = tokenize(profile.get('campus', ''))

    # Gabungkan semua data kandidat untuk dicek tokennya
    full_text = f"{candidate['name']} {candidate['org']} {candidate['bio']}"
    result_tokens = set(tokenize(full_text))

    def count_hits(target_tokens):
        return sum(1 for t in target_tokens if t in result_tokens)

    name_hits = count_hits(name_tokens)
    program_hits = count_hits(program_tokens)
    campus_hits = count_hits(campus_tokens)

    # Hitung Skor (Weighting sesuai logic JS)
    raw = (name_hits * 18) + (program_hits * 8) + (campus_hits * 8)
    
    # Source Weight untuk metadata akademik (OpenAlex = 1.15)
    final_score = min(round(raw * 1.15), 100) 

    reasons = []
    if name_hits: reasons.append(f"nama({name_hits})")
    if program_hits: reasons.append(f"prodi({program_hits})")
    if campus_hits: reasons.append(f"kampus({campus_hits})")

    return final_score, ", ".join(reasons) if reasons else "-"

# --- SISTEM SCHEDULER / TRACKER ---

def run_tracking_system():
    print("\n" + "="*40)
    print("🎓 ALUMNI TRACKER ENGINE (V.3 - FINAL)")
    print("="*40)
    
    nama_target = input("Masukkan Nama Alumni: ").strip()
    kampus_target = input("Masukkan Nama Kampus: ").strip()
    prodi_target = input("Masukkan Jurusan/Prodi: ").strip()

    # 1. Crawl & Ekstraksi Data
    candidates = scrape_alumni_data(nama_target, kampus_target)
    
    # 2. Scoring & Disambiguation
    best_cand = None
    best_score = 0
    best_reasons = "-"

    profile = {'name': nama_target, 'major': prodi_target, 'campus': kampus_target}

    for cand in candidates:
        score, reasons = score_evidence(profile, cand)
        if score > best_score:
            best_score = score
            best_cand = cand
            best_reasons = reasons

    # 3. Decision Engine & Supabase Update
    # Threshold: Strong >= 65, Weak >= 40
    status = "Tidak Ditemukan"
    if best_cand and best_score >= 40:
        status = "Teridentifikasi" if best_score >= 65 else "Perlu Verifikasi Manual"
        
        data_to_upsert = {
            "name": nama_target,
            "campus": kampus_target,
            "major": prodi_target,
            "status": status,
            "confidence_score": best_score,
            "evidence_url": best_cand['link'],
            "last_update": "now()"
        }

        try:
            # Gunakan upsert agar data tidak duplikat di Supabase
            supabase.table("alumni").upsert(data_to_upsert, on_conflict="name").execute()
            print(f"\n✅ DATA DIUPDATE KE SUPABASE")
            print(f"📊 Hasil: {status} ({best_score}/100)")
            print(f"📝 Alasan: {best_reasons}")
        except Exception as e:
            print(f"❌ Error Supabase: {e}")
    else:
        print(f"\n❌ Skor terlalu rendah ({best_score}). Data ditolak sistem.")

if __name__ == "__main__":
    run_tracking_system()