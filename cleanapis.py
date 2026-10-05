"""
cleanapis.py: login ke CleanAPIs (via Google) + buat API key.

Fungsi:
  - login_cleanapis(page, email, password) -> True kalau sudah di dashboard
  - buat_api_key(page, email) -> api_key (string) atau None kalau gagal
"""

from __future__ import annotations

import os
import sys
import time

from playwright.sync_api import Page

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tampilan

_START = "https://cleanapis.com/?ref=CC9ELETL"
_KEYS_URL = "https://cleanapis.com/dashboard/api-keys"

# kata "batal" dalam banyak bahasa (jangan diklik)
KATA_BATAL = (
    "cancel", "cancelar", "abbrechen", "annuler", "annulla", "отмена",
    "batal", "batalkan", "no thanks", "not now", "maybe later", "later",
    "tidak", "nanti", "no", "nein", "non", "não", "否", "取消", "취소",
    "back", "zurück", "retour", "atrás", "kembali", "返回", "뒤로",
    "deny", "refuse", "reject", "decline",
    # jangan klik tombol top-up / harga (pernah terjadi: '$25', '30d')
    "$", "rp", "usd", "idr", "top up", "topup", "isi ulang", "beli", "buy",
    "purchase", "price", "harga", "upgrade", "langganan", "subscribe",
    "plan", "paket", "credit", "saldo", "bulan", "month", "year", "tahun",
)

INFO_TOMBOL_JS = """() => {
    const sem = Array.from(document.querySelectorAll('button, [role="button"], a[role="button"]'));
    const hasil = [];
    for (let i = 0; i < sem.length; i++) {
        const b = sem[i];
        const rect = b.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;
        const st = window.getComputedStyle(b);
        const bg = st.backgroundColor;
        const m = bg.match(/[0-9.]+/g);
        let r = 255, g = 255, bl = 255;
        if (m && m.length >= 3) { r = +m[0]; g = +m[1]; bl = +m[2]; }
        const mx = Math.max(r, g, bl), mn = Math.min(r, g, bl);
        hasil.push({
            i: i,
            teks: (b.innerText || b.textContent || '').trim().slice(0, 60),
            berwarna: (mx - mn) > 40 && mx > 100,
            biru: bl > r + 20 && bl > g + 20,
            area: Math.round(rect.width * rect.height),
        });
    }
    return hasil;
}"""


def _klik_tombol_google(page: Page) -> str | None:
    """
    Klik tombol utama Google (selalu berwarna, biasanya biru), bahasa apa pun.

    Hanya boleh dipanggil saat masih di domain accounts.google.com.
    Kembalikan teks tombol yang diklik, atau None.
    """
    if "accounts.google" not in (page.url or ""):
        return None
    try:
        info = page.evaluate(INFO_TOMBOL_JS)
    except Exception:
        return None
    if not info:
        return None

    kandidat = []
    for b in info:
        teks = (b["teks"] or "").strip().lower()
        if not teks:
            continue
        if any(k in teks for k in KATA_BATAL):
            continue
        # jangan klik link merk/nama domain (contoh: "cleanapis.com")
        if "." in teks and " " not in teks and len(teks) < 30:
            continue
        skor = 0
        if b["biru"]:
            skor += 20
        elif b["berwarna"]:
            skor += 8
        skor += min(3, b["area"] // 5000)
        kandidat.append((skor, b["i"], teks))
    if not kandidat:
        return None

    kandidat.sort(key=lambda x: (x[0], x[1]))
    skor, idx, teks = kandidat[-1]
    try:
        page.evaluate(f"""() => {{
            const sem = document.querySelectorAll('button, [role="button"], a[role="button"]');
            sem[{idx}].click();
        }}""")
    except Exception:
        return None
    tampilan.log("INFO", f"klik tombol Google: '{teks[:30]}'")
    return teks


def _selesai_login(page: Page) -> bool:
    """
    True kalau sudah sampai domain CleanAPIs (bukan halaman Google/auth lagi).

    Tunggu sampai keluar dari Google saja - halaman dashboard bisa saja belum
    selesai render, tapi buat_api_key() akan langsung goto /dashboard/api-keys.
    """
    url = page.url or ""
    if "accounts.google" in url:
        return False
    if "cleanapis.com" not in url:
        return False
    # masih di halaman daftar/masuk -> belum selesai
    if "/register" in url or "/login" in url:
        return False
    return True


def _klik_email_sendiri(page: Page, email: str) -> bool:
    """
    Di layar 'pilih akun' Google, klik baris yang berisi email ATAU nama
    (email bisa juga ditulis dg titik/digaris-bawahkan - Google kadang
    hanya menampilkan nama, jadi cocokkan bagian lokal email).
    """
    # bagian lokal email: 'olga.nugraha' -> kata kunci 'olga' dan 'nugraha'
    lokal = email.split("@")[0].replace(".", " ").replace("_", " ")
    kunci = [k for k in lokal.split() if len(k) >= 4]

    try:
        info = page.evaluate("""(email, kunci) => {
            const sem = Array.from(document.querySelectorAll(
                'a, button, [role="link"], [role="button"], div, li'
            ));
            // 1. cari baris berisi email penuh dulu
            for (const b of sem) {
                const t = (b.innerText || b.textContent || '').trim();
                if (t.toLowerCase().includes(email.toLowerCase())) {
                    const r = b.getBoundingClientRect();
                    if (r.width === 0 || r.height === 0) continue;
                    return t.slice(0, 60);
                }
            }
            // 2. cari baris berisi semua kata kunci dari lokal email
            if (kunci.length) {
                for (const b of sem) {
                    const t = (b.innerText || b.textContent || '').trim().toLowerCase();
                    if (!t) continue;
                    const r = b.getBoundingClientRect();
                    if (r.width === 0 || r.height === 0) continue;
                    if (t.includes('@')) continue;  // ini akun lain
                    if (kunci.every(k => t.includes(k))) return t.slice(0, 60);
                }
            }
            return null;
        }""", [email, kunci])
    except Exception:
        return False
    if not info:
        return False
    try:
        page.get_by_text(info.split("\n")[0], exact=False).first.click(timeout=10_000)
        tampilan.log("INFO", f"klik akun '{info.split(chr(10))[0]}' ...")
        return True
    except Exception:
        return False


def login_cleanapis(page: Page, email: str, password: str) -> bool:
    """
    Daftar/login CleanAPIs lewat Sign up with Google sampai masuk dashboard.

    Untuk akun baru: setelah password ada layar consent 'Login ke cleanapis.com'
    yang harus diklik Lanjutkan. Untuk akun lama: langsung ke dashboard.
    Kembalikan True kalau sukses.
    """
    tampilan.log("INFO", "buka halaman reff CleanAPIs ...")
    page.goto(_START, wait_until="domcontentloaded")
    time.sleep(2)

    tampilan.log("INFO", "klik 'Get Started' ...")
    page.get_by_role("link", name="Get Started").click()
    time.sleep(2)

    tampilan.log("INFO", "klik 'Sign up with Google' ...")
    page.get_by_role("link", name="Sign up with Google").click()
    time.sleep(4)

    # ---- isi email ----
    tampilan.log("INFO", f"isi email {email} ...")
    field_email = page.locator("input#identifierId")
    field_email.wait_for(state="visible", timeout=60_000)
    field_email.fill(email)
    time.sleep(1)
    _klik_tombol_google(page)
    time.sleep(4)

    # ---- isi password ----
    tampilan.log("INFO", "isi password ...")
    field_pw = page.locator("input[name='Passwd']")
    field_pw.wait_for(state="visible", timeout=60_000)
    field_pw.fill(password)
    time.sleep(1)
    _klik_tombol_google(page)
    time.sleep(5)

    # ---- loop consent / pilih akun sampai keluar dari Google ----
    tampilan.log("INFO", "deteksi layar konfirmasi Google ...")
    for percobaan in range(1, 13):
        if _selesai_login(page):
            tampilan.log("OK", "sudah masuk dashboard CleanAPIs")
            break
        url = page.url or ""
        if "accountchooser" in url:
            if _klik_email_sendiri(page, email):
                time.sleep(4)
                continue
        if _klik_tombol_google(page):
            time.sleep(4)
        else:
            tampilan.log("INFO", f"(percobaan {percobaan}) tidak ada tombol, tunggu ...")
            # diagnostik: tampilkan URL + potongan teks layar
            if percobaan % 3 == 0:
                try:
                    potong = (page.inner_text("body") or "").replace("\n", " ")[:120]
                except Exception:
                    potong = "<gagal baca body>"
                tampilan.log("INFO", f"  URL  : {url}")
                tampilan.log("INFO", f"  teks : {potong}")
            time.sleep(3)

    ok = _selesai_login(page)
    if ok:
        tampilan.log("OK", "login CleanAPIs SUKSES")
    else:
        tampilan.log("ERROR", "login CleanAPIs GAGAL")
    return ok


def buat_api_key(page: Page, email: str) -> str | None:
    """
    Buka halaman API Keys, klik Create API Key, isi Key Name dengan email,
    ambil key baru, lalu klik 'Copy key' (sebagai konfirmasi).
    """
    # pastikan ada di halaman API Keys CleanAPIs (bisa saja lagi di 9Router
    # karena loop percobaan ulang)
    if "cleanapis.com/dashboard/api-keys" not in (page.url or ""):
        tampilan.log("INFO", "buka halaman API Keys ...")
        page.goto(_KEYS_URL, wait_until="domcontentloaded")
        time.sleep(3)

    tampilan.log("INFO", "klik 'Create API Key' ...")
    page.get_by_role("button", name="Create API Key").click()
    time.sleep(2)

    tampilan.log("INFO", f"isi Key Name: {email} ...")
    field_nama = page.locator("input#name")
    field_nama.wait_for(state="visible", timeout=30_000)
    field_nama.fill(email)
    time.sleep(0.5)

    tampilan.log("INFO", "klik 'Create Key' (submit) ...")
    page.get_by_role("button", name="Create Key").click()
    time.sleep(4)

    # ---- ambil key ----
    api_key = _ambil_api_key(page)
    if api_key:
        tampilan.log("OK", f"API key didapat: {api_key[:12]}... ({len(api_key)} char)")
        # Klik 'Copy key' supaya banner hilang & key tercatat.
        try:
            page.get_by_role("button", name="Copy key").click(timeout=10_000)
            time.sleep(1)
        except Exception:
            pass
    else:
        tampilan.log("ERROR", "GAGAL: API key tidak ditemukan di layar")
    return api_key


def _ambil_api_key(page: Page) -> str | None:
    """
    Ambil API key baru dari banner 'YOUR NEW API KEY'.

    Key ditampilkan sekali saja dalam elemen <code> dengan teks polos cc_...
    (di list table key ditampilkan teredaksi: cc_xxxx••••, jadi BUKAN sumbernya).
    """
    for putaran in range(20):
        try:
            hasil = page.evaluate("""() => {
                for (const el of document.querySelectorAll('code, pre, input, textarea, span, div, p')) {
                    const t = (el.value || el.textContent || '').trim();
                    if (/^cc_[A-Za-z0-9]{20,}$/.test(t)) return t;
                }
                return null;
            }""")
        except Exception:
            hasil = None
        if hasil:
            return hasil
        time.sleep(1)
    return None
