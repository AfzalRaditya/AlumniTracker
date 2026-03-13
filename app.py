import streamlit as st
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv
from tracker import score_evidence, tokenize
from scraper_engine import scrape_alumni_data

# Konfigurasi
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Alumni Tracker", layout="wide")

# --- FUNGSI LOGIN ADMIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.subheader("🔑 Login Admin")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "admin123":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Password Salah")
        return False
    return st.session_state["password_correct"]

# --- NAVBAR TABS ---
tab1, tab2 = st.tabs(["🌐 Halaman Pengunjung", "🛠️ Panel Admin"])

# --- TAB 1: PENGUNJUNG ---
with tab1:
    st.title("🎓 Database Alumni")
    try:
        res = supabase.table("alumni").select("*").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data)[["name", "campus", "major", "status", "confidence_score"]], use_container_width=True)
    except: st.info("Belum ada data.")

# --- TAB 2: ADMIN ---
with tab2:
    if check_password():
        st.title("🛠️ Admin Management")
        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.rerun()

        st.divider()

        # FORM PENCARIAN
        st.subheader("🔍 Lacak Alumni Baru")
        with st.form("search_alumni"):
            c1, c2, c3 = st.columns(3)
            search_name = c1.text_input("Nama Lengkap")
            search_campus = c2.text_input("Kampus", value="Universitas Muhammadiyah Malang")
            search_major = c3.text_input("Jurusan")
            btn_search = st.form_submit_button("Mulai Lacak")

        # PROSES PENCARIAN (TIDAK LANGSUNG SIMPAN)
        if btn_search:
            if search_name:
                with st.spinner("Mencari hasil yang mendekati..."):
                    results = scrape_alumni_data(search_name, search_campus)
                    if results:
                        st.session_state["search_results"] = results
                        st.session_state["target_profile"] = {"name": search_name, "campus": search_campus, "major": search_major}
                    else:
                        st.error("Tidak ditemukan hasil yang cocok.")
            else:
                st.warning("Masukkan nama alumni.")

        # MENAMPILKAN HASIL UNTUK DIPILIH (PREVIEW MODE)
        if "search_results" in st.session_state:
            st.subheader("📋 Hasil yang Mendekati (Pilih untuk Simpan)")
            target = st.session_state["target_profile"]
            
            for i, cand in enumerate(st.session_state["search_results"]):
                score, reasons = score_evidence(target, cand)
                
                with st.expander(f"Hasil #{i+1}: {cand['name']} (Skor: {score}%)", expanded=(score > 60)):
                    col_info, col_action = st.columns([4, 1])
                    
                    with col_info:
                        st.write(f"**Institusi:** {cand['org']}")
                        st.write(f"**Detail:** {cand['bio']}")
                        st.caption(f"Kecocokan: {reasons}")
                        st.markdown(f"[Lihat Sumber Asli]({cand['link']})")
                    
                    with col_action:
                        # TOMBOL SIMPAN DATA INI
                        if st.button("✅ Simpan", key=f"save_{i}"):
                            status = "Teridentifikasi" if score >= 65 else "Perlu Verifikasi"
                            save_data = {
                                "name": target['name'], # Gunakan nama input admin agar rapi
                                "campus": target['campus'],
                                "major": target['major'],
                                "status": status,
                                "confidence_score": score,
                                "evidence_url": cand['link']
                            }
                            supabase.table("alumni").upsert(save_data, on_conflict="name").execute()
                            st.success(f"Data {cand['name']} disimpan!")
                            del st.session_state["search_results"] # Bersihkan hasil setelah simpan
                            st.rerun()
            
            if st.button("❌ Batalkan Pencarian"):
                del st.session_state["search_results"]
                st.rerun()

        st.divider()

        # FITUR HAPUS DATA (SAMA SEPERTI SEBELUMNYA)
        st.subheader("🗑️ Kelola Database")
        try:
            res_db = supabase.table("alumni").select("*").execute()
            df_db = pd.DataFrame(res_db.data)
            for _, row in df_db.iterrows():
                col_n, col_d = st.columns([4, 1])
                col_n.write(f"**{row['name']}** - {row['major']}")
                if col_d.button("Hapus", key=f"db_{row['name']}"):
                    supabase.table("alumni").delete().eq("name", row['name']).execute()
                    st.rerun()
        except: pass