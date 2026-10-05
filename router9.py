"""
router9.py: login ke 9Router + (sekali) buat provider CleanAPIs + tambah API key.

Fungsi:
  - login_router(page, password) -> True kalau sudah di dashboard
  - pastikan_provider(page) -> True kalau provider CleanAPIs siap dipakai
  - tambah_koneksi(page, nama, api_key) -> "ok" | "sudah_ada" | "invalid" | "gagal"
"""

from __future__ import annotations

import os
import sys
import time

from playwright.sync_api import Page

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tampilan

_LOGIN = "http://localhost:20128/login"
_PROVIDERS = "http://localhost:20128/dashboard/providers"

# konstanta provider CleanAPIs (dipakai untuk "buat sekali saja")
NAMA_PROVIDER = "CleanAPIs"
PREFIX_PROVIDER = "cleanapis"
BASE_URL_PROVIDER = "https://cleanapis.com/v1"
DEFAULT_MODEL = "default"


def atur_url(base: str) -> None:
    """Ganti URL dasar 9Router (dipanggil dari main.py sesuai .env)."""
    global _LOGIN, _PROVIDERS
    base = base.rstrip("/")
    _LOGIN = f"{base}/login"
    _PROVIDERS = f"{base}/dashboard/providers"


def _sudah_login(page: Page) -> bool:
    """Cek apakah halaman sudah menampilkan dashboard (menu Providers)."""
    try:
        teks = page.inner_text("body")
    except Exception:
        return False
    return "Providers" in teks and "Enter your password" not in teks


def login_router(page: Page, password: str) -> bool:
    """Login ke dashboard 9Router. Kembalikan True kalau sukses."""
    tampilan.log("INFO", f"buka halaman login 9Router ({_LOGIN}) ...")
    try:
        page.goto(_LOGIN, wait_until="domcontentloaded", timeout=30_000)
    except Exception as err:
        tampilan.log("ERROR", f"TIDAK BISA BUKA {_LOGIN}")
        tampilan.log("ERROR", f"cek apakah 9Router jalan & URL benar ({type(err).__name__})")
        return False
    time.sleep(1)

    # SPA butuh waktu render. Tunggu sampai muncul form password (perlu login)
    # atau menu dashboard (sudah login). Maksimal 30 detik.
    for _ in range(60):
        try:
            if "Loading" not in (page.inner_text("body") or ""):
                break
        except Exception:
            pass
        time.sleep(0.5)

    # kalau sudah login (cookie masih aktif), halaman langsung tampil dashboard
    if _sudah_login(page):
        tampilan.log("OK", "sudah login 9Router (sesi masih aktif)")
        return True

    tampilan.log("INFO", "tunggu field password ...")
    field = page.locator("input[type='password']")
    field.wait_for(state="visible", timeout=30_000)

    tampilan.log("INFO", "isi password ...")
    field.fill(password)
    time.sleep(0.5)
    try:
        page.get_by_role("button", name="Login").click(timeout=15_000)
    except Exception:
        tampilan.log("WARN", "klik Login lambat, coba Enter ...")
        try:
            field.press("Enter")
        except Exception:
            pass
    time.sleep(4)

    if _sudah_login(page):
        tampilan.log("OK", "login 9Router SUKSES")
        return True

    tampilan.log("ERROR", f"login 9Router GAGAL -> {page.url}")
    tampilan.log("ERROR", "cek ROUTER_PASSWORD di file .env")
    return False


def _provider_ada(page: Page) -> bool:
    """Cek apakah provider 'CleanAPIs' sudah ada — tahan kalau SPA masih Loading."""
    for _ in range(12):
        try:
            body = page.inner_text("body") or ""
        except Exception:
            time.sleep(0.5)
            continue
        if "Loading" in body:
            time.sleep(0.5)
            continue
        # link OR teks — yang mana duluan yang muncul
        try:
            if page.get_by_role("link", name=NAMA_PROVIDER).count() > 0:
                return True
        except Exception:
            pass
        if NAMA_PROVIDER in body:
            return True
        return False
    return False


def _buka_detail_provider(page: Page) -> bool:
    """Buka halaman detail provider CleanAPIs. Kembalikan True kalau berhasil."""
    tampilan.log("INFO", f"buka providers -> klik '{NAMA_PROVIDER}' ...")
    page.goto(_PROVIDERS, wait_until="domcontentloaded")
    time.sleep(3)
    try:
        page.get_by_role("link", name=NAMA_PROVIDER).first.click(timeout=20_000)
        time.sleep(3)
        return True
    except Exception as err:
        tampilan.log("ERROR", f"gagal klik provider '{NAMA_PROVIDER}': {err}")
        return False


def _buat_provider(page: Page) -> bool:
    """
    Buat provider CleanAPIs (Add OpenAI Compatible). SEKALI SAJA.
    Dipanggil kalau provider belum ada. Kembalikan True kalau sukses.
    """
    tampilan.log("INFO", "klik 'Add OpenAI Compatible' ...")
    try:
        page.get_by_role("button", name="Add OpenAI Compatible").click(timeout=20_000)
    except Exception as err:
        tampilan.log("ERROR", f"gagal klik 'Add OpenAI Compatible': {err}")
        return False
    time.sleep(2)

    # ---- isi form ----
    tampilan.log("INFO", f"isi Name: {NAMA_PROVIDER} ...")
    f = page.locator("input[placeholder='OpenAI Compatible (Prod)']")
    f.wait_for(state="visible", timeout=15_000)
    f.fill(NAMA_PROVIDER)
    time.sleep(0.5)

    tampilan.log("INFO", f"isi Prefix: {PREFIX_PROVIDER} ...")
    page.locator("input[placeholder='oc-prod']").fill(PREFIX_PROVIDER)
    time.sleep(0.5)

    tampilan.log("INFO", f"isi Base URL: {BASE_URL_PROVIDER} ...")
    page.locator("input[placeholder='https://api.openai.com/v1']").fill(BASE_URL_PROVIDER)
    time.sleep(0.5)

    tampilan.log("INFO", "klik Create ...")
    try:
        page.get_by_role("button", name="Create").click(timeout=30_000)
    except Exception as err:
        tampilan.log("ERROR", f"gagal klik Create: {err}")
        return False
    time.sleep(4)

    # cek apakah provider baru muncul
    if _provider_ada(page):
        tampilan.log("OK", f"provider '{NAMA_PROVIDER}' berhasil dibuat")
        return True
    tampilan.log("ERROR", f"provider '{NAMA_PROVIDER}' TIDAK muncul setelah Create")
    return False


def pastikan_provider(page: Page) -> bool:
    """
    Pastikan provider CleanAPIs ADA & halaman detailnya terbuka.
    Kalau belum ada -> buat (sekali saja). Kalau sudah ada -> langsung klik.

    Kembalikan True kalau halaman detail sudah terbuka & siap tambah koneksi.
    """
    tampilan.log("INFO", f"buka halaman providers ({_PROVIDERS}) ...")
    page.goto(_PROVIDERS, wait_until="domcontentloaded")
    time.sleep(3)

    if not _provider_ada(page):
        tampilan.log("INFO", f"provider '{NAMA_PROVIDER}' belum ada -> buat dulu")
        if not _buat_provider(page):
            return False
        time.sleep(2)
        # setelah create, pastikan benar-benar ada
        page.goto(_PROVIDERS, wait_until="domcontentloaded")
        time.sleep(3)
        if not _provider_ada(page):
            tampilan.log("ERROR", f"provider '{NAMA_PROVIDER}' masih tidak ada")
            return False
    else:
        tampilan.log("OK", f"provider '{NAMA_PROVIDER}' sudah ada")

    return _buka_detail_provider(page)


def _teks_dialog(page: Page) -> str | None:
    """Ambil teks HANYA dari dialog 'Add API Key' yang sedang terbuka."""
    try:
        return page.evaluate("""() => {
            let d = document.querySelector('[role="dialog"]');
            if (d) return (d.textContent || '').trim();
            const modal = document.querySelectorAll('.ant-modal, .modal, [class*="modal"], [class*="dialog"]');
            if (modal.length) return (modal[modal.length-1].textContent || '').trim();
            return null;
        }""")
    except Exception:
        return None


def _tutup_dialog(page: Page) -> None:
    """Tutup dialog Add API Key tanpa menyimpan (klik Cancel / X)."""
    for nama in ("Cancel", "✕", "Close"):
        try:
            b = page.get_by_role("button", name=nama)
            if b.count() > 0 and b.first.is_visible():
                b.first.click()
                time.sleep(1)
                return
        except Exception:
            continue


def _koneksi_ada(page: Page, nama: str) -> bool:
    """Cari apakah nama koneksi sudah ada di list Connections."""
    try:
        return nama in (page.inner_text("body") or "")
    except Exception:
        return False


def _hapus_koneksi(page: Page, nama: str) -> bool:
    """Hapus koneksi bernama 'nama' dari list (ganti key baru, anti duplikat)."""
    # baris koneksi: <p> berisi nama, lalu tombol delete setelahnya
    p_nama = page.locator(f"p:has-text('{nama}')")
    if p_nama.count() == 0:
        return False
    del_btn = p_nama.locator("xpath=following::button[contains(.,'delete')]")
    if del_btn.count() == 0:
        return False
    try:
        del_btn.first.click()
        time.sleep(2)
        # konfirmasi hapus
        try:
            page.get_by_role("button", name="Confirm").click(timeout=10_000)
            time.sleep(3)
        except Exception:
            pass
        return True
    except Exception:
        return False


def tambah_koneksi(
    page: Page, nama: str, api_key: str, ganti_ada: bool = True
) -> str:
    """
    Tambah koneksi API key ke provider CleanAPIs.

    ganti_ada=True (mode full, key baru):
      - kalau nama SUDAH ada -> HAPUS koneksi lama, lalu daftarkan ulang
        pakai key baru (supaya TIDAK ADA duplikat).
    ganti_ada=False (mode 3, import key):
      - kalau nama SUDAH ada -> kembalikan "sudah_ada" (tidak input ulang)

    Kembalikan:
      "ok"        -> tersimpan & lolos Check
      "sudah_ada" -> nama koneksi sudah ada (hanya mode 3)
      "invalid"   -> API key ditolak (perlu buat key baru)
      "gagal"     -> masalah lain
    """
    # pastikan ada di halaman detail provider
    if NAMA_PROVIDER not in (page.inner_text("body") or ""):
        if not _buka_detail_provider(page):
            return "gagal"
    time.sleep(1)

    # ---- CEK NAMA: kalau sudah ada, tergantung mode ----
    if _koneksi_ada(page, nama):
        if not ganti_ada:
            tampilan.log("OK", f"nama '{nama}' sudah ada di 9Router -> lewati")
            return "sudah_ada"
        tampilan.log("INFO", f"nama '{nama}' sudah ada -> hapus dulu, ganti key baru")
        if not _hapus_koneksi(page, nama):
            tampilan.log("ERROR", f"gagal hapus koneksi lama '{nama}' -> lewati")
            return "gagal"
        time.sleep(2)
        if _koneksi_ada(page, nama):
            tampilan.log("ERROR", f"'{nama}' masih ada setelah hapus -> lewati")
            return "gagal"
        tampilan.log("OK", f"koneksi lama '{nama}' dihapus")

    tampilan.log("INFO", "klik 'Add API Key' ...")
    try:
        page.get_by_role("button", name="Add API Key").first.click(timeout=20_000)
    except Exception as err:
        tampilan.log("ERROR", f"gagal klik 'Add API Key': {err}")
        return "gagal"
    time.sleep(3)

    # ---- isi form ----
    tampilan.log("INFO", f"isi Nama: {nama} ...")
    field_nama = page.locator("input[placeholder='Production Key']")
    field_nama.wait_for(state="visible", timeout=15_000)
    field_nama.fill(nama)
    time.sleep(0.5)

    tampilan.log("INFO", f"isi API Key: {api_key[:12]}... ({len(api_key)} char)")
    field_key = page.locator("input[type='password']")
    field_key.wait_for(state="visible", timeout=10_000)
    field_key.fill(api_key)
    time.sleep(0.5)

    tampilan.log("INFO", f"isi Default Model: {DEFAULT_MODEL} ...")
    field_model = page.locator("input[placeholder='gpt-4o-mini']")
    field_model.wait_for(state="visible", timeout=10_000)
    field_model.fill(DEFAULT_MODEL)
    time.sleep(0.5)

    # ---- Check dulu untuk validasi key ----
    tampilan.log("INFO", "klik Check (validasi key) ...")
    try:
        page.get_by_role("button", name="Check").click(timeout=20_000)
    except Exception:
        tampilan.log("WARN", "tidak ada tombol Check, lanjut Save")
    else:
        time.sleep(4)
        hasil_check = _teks_dialog(page)
        if hasil_check and "invalid" in hasil_check.lower():
            tampilan.log("ERROR", "key DITOLAK (Invalid)")
            _tutup_dialog(page)
            return "invalid"
        tampilan.log("OK", "key lolos Check")

    # ---- Save ----
    tampilan.log("INFO", "klik Save ...")
    try:
        page.get_by_role("button", name="Save").click(timeout=20_000)
    except Exception as err:
        tampilan.log("ERROR", f"gagal klik Save: {err}")
        return "gagal"
    time.sleep(4)

    # ---- cek hasil ----
    ok = _koneksi_ada(page, nama)
    if ok:
        tampilan.log("OK", f"koneksi '{nama}' TERSIMPAN")
    else:
        tampilan.log("ERROR", f"koneksi '{nama}' TIDAK YAKIN - periksa manual")
    return "ok" if ok else "gagal"
