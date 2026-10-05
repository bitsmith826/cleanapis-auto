"""
tampilan.py: utilitas output ke console - warna, layout, progress bar modern.
Tetap kompatibel Windows cmd (ANSI + UTF-8, tanpa library tambahan).
"""
from __future__ import annotations
import ctypes
import os
import sys
import time
import unicodedata

LEBAR = 60
LOG_PATH = None

CYN = "\033[36m"
GRN = "\033[32m"
RED = "\033[31m"
YEL = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RST = "\033[0m"

BCYN = "\033[96m"
BGRN = "\033[92m"
BRED = "\033[91m"
BYEL = "\033[93m"
BBLU = "\033[94m"
WHT = "\033[97m"

BG_BLU = "\033[44m"
BG_GRN = "\033[42m"
BG_RED = "\033[41m"
BG_YEL = "\033[43m"
BG_DIM = "\033[100m"

_BADGE = {
    "INFO":  BG_BLU + WHT + BOLD,
    "OK":    BG_GRN + WHT + BOLD,
    "WARN":  BG_YEL + "\033[30m" + BOLD,
    "ERROR": BG_RED + WHT + BOLD,
    "DEBUG": BG_DIM + WHT + BOLD,
}
_IKON = {"INFO": "\u25cf", "OK": "\u2714", "WARN": "\u26a0", "ERROR": "\u2718"}

def aktifkan_warna() -> None:
    if sys.platform != "win32":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def atur_log_file(path):
    global LOG_PATH
    LOG_PATH=path
    if path:
        try: os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        except: pass
def _tulis_log_file(teks):
    if not LOG_PATH: return
    try: open(LOG_PATH,"a",encoding="utf-8").write(teks+chr(10))
    except: pass
def _lebar_tampilan(teks: str) -> int:
    total = 0
    for ch in teks:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        elif unicodedata.category(ch) in ("Mn", "Me"):
            pass
        else:
            total += 1
    return total

def _tengah(teks: str) -> str:
    isi = f" {teks} "
    sisa = LEBAR - _lebar_tampilan(isi)
    if sisa < 0:
        return isi
    kiri = sisa // 2
    return " " * kiri + isi + " " * (sisa - kiri)

# -- judul & garis --

def judul(teks: str) -> None:
    print(BOLD + BCYN + "\u256d" + "\u2500" * LEBAR + "\u256e" + RST)
    isi = f" \u26a1  {teks} "
    sisa = LEBAR - _lebar_tampilan(isi)
    kiri = sisa // 2
    tengah = " " * kiri + isi + " " * (sisa - kiri)
    print(BOLD + BCYN + "\u2502" + RST + BOLD + WHT + tengah + RST + BOLD + BCYN + "\u2502" + RST)
    print(BOLD + BCYN + "\u2570" + "\u2500" * LEBAR + "\u256f" + RST)

def garis() -> None:
    print(DIM + "\u2500" * LEBAR + RST)

def garis_tebal() -> None:
    print(DIM + "\u2501" * LEBAR + RST)

# -- progress bar --

def _bar(n: int, total: int, lebar: int = 20) -> str:
    if total <= 0:
        return DIM + "\u2591" * lebar + RST
    pct = max(0.0, min(1.0, n / total))
    isi = round(pct * lebar)
    if pct >= 1.0:
        warna = BGRN
    elif pct >= 0.5:
        warna = BCYN
    else:
        warna = BYEL
    return warna + "\u2588" * isi + RST + DIM + "\u2591" * (lebar - isi) + RST

def progress_bar(n: int, total: int, lebar: int = 20) -> str:
    pct = 0 if total == 0 else n / total * 100
    return f"{_bar(n, total, lebar)} {DIM}{n}/{total}{RST} {BOLD}{pct:.0f}%{RST}"

# -- header blok akun --

def bilah(label: str, waktu: str = "", warna: str = BCYN) -> None:
    print(warna + "\u250c" + "\u2500" * LEBAR + "\u2510" + RST)
    kiri = f"  {label} "
    kanan = f" {waktu} " if waktu else ""
    # hitung padding tengah agar waktu nempel kanan
    isi_tengah = kiri + " " * max(0, LEBAR - _lebar_tampilan(kiri) - _lebar_tampilan(kanan)) + kanan
    # pad jika masih kurang (pembulatan)
    pad = LEBAR - _lebar_tampilan(isi_tengah)
    if pad > 0:
        isi_tengah += " " * pad
    print(warna + "\u2502" + RST + BOLD + WHT + isi_tengah + RST + warna + "\u2502" + RST)
    print(warna + "\u2514" + "\u2500" * LEBAR + "\u2518" + RST)

# -- log --

def log(status: str, pesan: str) -> None:
    jam = time.strftime("%H:%M:%S")
    bg = _BADGE.get(status, BG_DIM + WHT + BOLD)
    ikon = _IKON.get(status, "\u00b7")
    badge = f"{bg} {ikon} {status:<5} {RST}"
    print(f"{DIM}{jam}{RST} {badge} {pesan}", flush=True)
    _tulis_log_file(f"{jam} [{status}] {pesan}")

def sukses(pesan: str) -> None:
    print(f"{BG_GRN + WHT + BOLD}  \u2714 SUKSES  {RST} {BGRN}{pesan}{RST}", flush=True)

def dilewati(pesan: str) -> None:
    print(f"{BG_DIM + WHT + BOLD}  \u00bb SKIP  {RST} {DIM}{pesan}{RST}", flush=True)

def gagal(pesan: str) -> None:
    print(f"{BG_RED + WHT + BOLD}  \u2718 GAGAL  {RST} {BRED}{pesan}{RST}", flush=True)

# -- ringkasan --

def ringkasan(berhasil: int, skip: int, error: int) -> None:
    total = berhasil + skip + error
    # header
    print(BOLD + BGRN + "\u256d" + "\u2500" * LEBAR + "\u256e" + RST)
    print(BOLD + BGRN + "\u2502" + RST + BOLD + WHT + _tengah("\u2726  RINGKASAN  \u2726") + RST + BOLD + BGRN + "\u2502" + RST)
    print(BOLD + BGRN + "\u251c" + "\u2500" * LEBAR + "\u2524" + RST)
    # baris progress - lebar bar disesuaikan agar "  BAR  97%" pas di dalam box
    pct = 0 if total == 0 else berhasil / total * 100
    bar_lebar = LEBAR - 10  # "  " + bar + "  " + "100%"
    bar = _bar(berhasil, total if total else 1, lebar=bar_lebar)
    # susun: "  " + bar + "  " + "97%" + pad agar total pas
    pct_teks = f"{pct:.0f}%"
    # bar sudah ada warna, hitung lebar visual tanpa ANSI
    bar_visual = bar_lebar
    isi = f"  {bar}  {BOLD}{pct_teks}{RST}"
    # pad kanan agar pas LEBAR (hit bersandar: 2 spasi kiri + bar + 2 spasi + pct)
    visual_isi = 2 + bar_visual + 2 + len(pct_teks)
    pad = LEBAR - visual_isi
    if pad < 0:
        pad = 0
    print(BOLD + BGRN + "\u2502" + RST + isi + " " * pad + BOLD + BGRN + "\u2502" + RST)
    print(BOLD + BGRN + "\u251c" + "\u2500" * LEBAR + "\u2524" + RST)
    def _row(ikon: str, label: str, n: int, warna: str):
        kiri = f"  {ikon}  {label}"
        kanan = f"{n} "
        sisa2 = LEBAR - _lebar_tampilan(kiri) - _lebar_tampilan(kanan)
        isi2 = kiri + " " * max(1, sisa2) + kanan
        return BOLD + BGRN + "\u2502" + RST + warna + isi2 + RST + BOLD + BGRN + "\u2502" + RST
    print(_row("\u2714", "Berhasil", berhasil, BGRN))
    print(_row("\u00bb", "Dilewati", skip, DIM))
    print(_row("\u2718", "Gagal", error, BRED if error else DIM))
    print(BOLD + BGRN + "\u2570" + "\u2500" * LEBAR + "\u256f" + RST)

# -- durasi & estimasi --

def _fmt_dur(detik: float) -> str:
    detik = int(detik)
    if detik < 60:
        return f"{detik} detik"
    if detik < 3600:
        return f"{detik // 60} menit"
    jam = detik // 3600
    sisa = (detik % 3600) // 60
    if sisa == 0:
        return f"{jam} jam"
    return f"{jam} jam {sisa} menit"

def estimasi_progres(index: int, total: int, mulai: float, selesai: int) -> None:
    if selesai == 0:
        return
    berjalan = time.time() - mulai
    rata = berjalan / selesai
    sisa = (total - index + 1) * rata
    pct = selesai / total * 100
    bar = _bar(selesai, total, lebar=14)
    log("INFO", f"{bar} {selesai}/{total} ({pct:.0f}%)  \u00b7  rata-rata {_fmt_dur(rata)}/akun  \u00b7  sisa ~{_fmt_dur(sisa)}")

def estimasi_ringkasan(mulai: float) -> None:
    if not mulai:
        return
    print(DIM + "\u2500" * LEBAR + RST)
    log("INFO", f"total waktu {_fmt_dur(time.time() - mulai)}  \u00b7  selesai {time.strftime('%H:%M:%S')}")
