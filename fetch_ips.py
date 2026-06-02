import requests, os
from datetime import datetime

API_BASE = "https://siberguvenlik.gov.tr/api/address/index"
OUT_FILE = "docs/edl.txt"

os.makedirs("docs", exist_ok=True)

session = requests.Session()
r = session.get(API_BASE, params={"type": "ip", "page": 0}, timeout=20)
r.raise_for_status()
data = r.json()
page_count = data.get("pageCount", 1)
print(f"Toplam kayıt: {data.get('totalCount')} | Sayfa: {page_count}")

seen, ips = set(), []
for page in range(page_count):
    try:
        r = session.get(API_BASE, params={"type": "ip", "page": page}, timeout=20)
        r.raise_for_status()
        for m in r.json().get("models", []):
            ip = m.get("url", "").strip()
            if ip and ip not in seen:
                seen.add(ip)
                ips.append(ip)
    except Exception as e:
        print(f"Sayfa {page} hata: {e}")
    if page % 100 == 99:
        print(f"  {page+1}/{page_count} sayfa, {len(ips)} IP")

updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
with open(OUT_FILE, "w") as f:
    f.write(f"# siberguvenlik.gov.tr EDL | Güncellendi: {updated}\n")
    f.write("\n".join(ips) + "\n")

print(f"Tamamlandı: {len(ips)} benzersiz IP → {OUT_FILE}")
