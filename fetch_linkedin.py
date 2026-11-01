"""Fetch your own LinkedIn outreach data via the Member Data Portability API.

Usage:
    Copy .env.example to .env and set LINKEDIN_TOKEN there, then:
    python fetch_linkedin.py

Writes linkedin_raw.json (stays on your machine) and prints only the FIELD NAMES
found in each domain, so you can share those without sharing any personal data.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def load_dotenv(path=".env"):
    """Load KEY=VALUE lines into the environment. Existing vars win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()
TOKEN = os.environ.get("LINKEDIN_TOKEN")
if not TOKEN:
    sys.exit("Set the LINKEDIN_TOKEN environment variable first.")

BASE = "https://api.linkedin.com/rest/memberSnapshotData"
DOMAINS = ["INVITATIONS", "CONNECTIONS", "INBOX"]  # case sensitive
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Linkedin-Version": "202312",  # the only version this endpoint supports
    "X-Restli-Protocol-Version": "2.0.0",
}
MAX_PAGES = 500


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_domain(domain):
    rows = []
    for start in range(MAX_PAGES):
        url = f"{BASE}?q=criteria&domain={domain}&start={start}"
        try:
            page = get(url)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            # The docs say to keep paging until an error says no data is left.
            if "No data found" in body:
                if start == 0:
                    print(f"  {domain}: no data yet (LinkedIn may still be processing it; retry later)")
                break
            print(f"  {domain}: HTTP {e.code} on page {start}: {body[:300]}")
            break
        found = 0
        for el in page.get("elements", []):
            data = el.get("snapshotData") or []
            rows.extend(data)
            found += len(data)
        if found == 0:
            break
    return rows


result = {}
for d in DOMAINS:
    print(f"Fetching {d} ...")
    result[d] = fetch_domain(d)
    keys = sorted({k for row in result[d] for k in row.keys()})
    print(f"  {len(result[d])} records")
    print(f"  fields: {keys}")

with open("linkedin_raw.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print("\nSaved linkedin_raw.json")
