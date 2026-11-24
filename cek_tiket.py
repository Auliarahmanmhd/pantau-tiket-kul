import os
import json
import urllib.request
import urllib.parse

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "").strip()

# Sesuaikan RAPIDAPI_HOST jika host API Google Flights yang lu pilih berbeda
RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST", "google-flights2.p.rapidapi.com").strip()

TARGETS = [
    {"origin": "KUL", "dest": "JED", "max_idr": 6_000_000, "durasi_hari": 12},
    {"origin": "KUL", "dest": "ALA", "max_idr": 5_800_000, "durasi_hari": 7},
    {"origin": "KUL", "dest": "IST", "max_idr": 7_500_000, "durasi_hari": 7},
]

# Sampel tanggal awal untuk Januari 2027 dan Desember 2028
SAMPLE_DATES = [
    "2027-01-10",
    "2028-12-15",
]


def kirim_telegram(pesan: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token atau Chat ID Telegram belum terisi.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": pesan,
        "parse_mode": "HTML",
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def cari_harga_tiket(origin: str, dest: str, outbound_date: str) -> dict:
    params = urllib.parse.urlencode({
        "departure_id": origin,
        "arrival_id": dest,
        "outbound_date": outbound_date,
        "currency": "IDR",
        "country": "ID",
        "travel_class": "economy",
    })
    url = f"https://{RAPIDAPI_HOST}/api/v1/searchFlights?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ekstrak_harga_terendah(data: dict):
    kandidat = []

    def telusuri(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in {"price", "lowest_price", "min_price", "amount"} and isinstance(v, (int, float)):
                    if v > 100_000:
                        kandidat.append(float(v))
                else:
                    telusuri(v)
        elif isinstance(obj, list):
            for item in obj:
                telusuri(item)

    telusuri(data)
    return min(kandidat) if kandidat else
