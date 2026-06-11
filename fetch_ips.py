import requests, os
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE  = "https://siberguvenlik.gov.tr/api/address/index?type=ip"
OUT_FILE  = "docs/edl.txt"
WORKERS   = 20

os.makedirs("docs", exist_ok=True)

session = requests.Session()
r = session.get(API_BASE, params={"type": "ip", "page": 0}, timeout=20)
r.raise_for_status()
page_count = r.json().get("pageCount", 1)

def fetch_page(page):
    try:
        r = session.get(API_BASE, params={"type": "ip", "page": page}, timeout=20)
        r.raise_for_status()
        return [m.get("url","").strip() for m in r.json().get("models",[]) if m.get("url")]
    except:
        return []

seen, ips = set(), []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for result in as_completed({ex.submit(fetch_page, p): p for p in range(page_count)}):
        for ip in result.result():
            if ip not in seen:
                seen.add(ip)
                ips.append(ip)

with open(OUT_FILE, "w") as f:
    f.write("\n".join(ips) + "\n")
