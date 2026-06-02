import requests, os
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
 
API_BASE  = "https://siberguvenlik.gov.tr/api/address/index"
OUT_FILE  = "docs/edl.txt"
WORKERS   = 20
 
os.makedirs("docs", exist_ok=True)
 
session = requests.Session()
r = session.get(API_BASE, params={"type": "ip", "page": 0}, timeout=20)
r.raise_for_status()
data       = r.json()
page_count = data.get("pageCount", 1)
print(f"Toplam kayıt: {data.get('totalCount')} | Sayfa: {page_count}")
 
def fetch_page(page):
    try:
        r = session.get(API_BASE, params={"type": "ip", "page": page}, timeout=20)
        r.raise_for_status()
        return [m.get("url","").strip() for m in r.json().get("models",[]) if m.get("url")]
    except Exception as e:
        print(f"Sayfa {page} hata: {e}")
        return []
 
seen, ips = set(), []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futures = {ex.submit(fetch_page, p): p for p in range(page_count)}
    done = 0
    for f in as_completed(futures):
        for ip in f.result():
            if ip not in seen:
                seen.add(ip)
                ips.append(ip)
        done += 1
        if done % 100 == 0:
            print(f"  {done}/{page_count} sayfa, {len(ips)} IP")
 
tr_tz   = timezone(timedelta(hours=3))
updated = datetime.now(tr_tz).strftime("%Y-%m-%d %H:%M TR")
 
with open(OUT_FILE, "w") as f:
    f.write(f"# siberguvenlik.gov.tr EDL | Güncellendi: {updated}\n")
    f.write("\n".join(ips) + "\n")
 
print(f"Tamamlandi: {len(ips)} benzersiz IP -> {OUT_FILE}")
