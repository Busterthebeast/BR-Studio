"""
BR Studio — Lead-processor.

Läser leads.csv, kvalificerar varje lead med automatisk scoring,
deduplicerar och sorterar efter prioritet.

Användning:
    python scripts/process_leads.py                          # processera alla
    python scripts/process_leads.py --bransch restaurang     # filtrera bransch
    python scripts/process_leads.py --min-score 50           # bara WARM+
    python scripts/process_leads.py --check-websites         # kör PageSpeed-check
    python scripts/process_leads.py --dry-run                # visa utan att spara

Kräver:
    pip install requests python-dotenv beautifulsoup4
"""

import argparse
import csv
import hashlib
import os
import socket
import ssl
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Installera beroenden: pip install requests python-dotenv beautifulsoup4")
    sys.exit(1)

load_dotenv()

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
LEADS_FILE = BASE_DIR / "cold-email" / "leads.csv"
OUTPUT_FILE = BASE_DIR / "cold-email" / "leads_scored.csv"
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")

# CSV-kolumner som vi förväntar oss (minst dessa)
REQUIRED_COLUMNS = ["company_name", "industry", "city"]

# Kolumner i output-filen
OUTPUT_COLUMNS = [
    "lead_id", "company_name", "industry", "industry_category",
    "contact_name", "contact_title", "email", "phone",
    "website_url", "address", "city", "postal_code",
    "google_rating", "review_count",
    "has_website", "has_ssl", "pagespeed_mobile",
    "lead_score", "lead_class",
    "source", "scraped_date",
    "status", "next_followup_date",
    "email_1_sent", "email_1_date",
    "email_2_sent", "email_2_date",
    "email_3_sent", "email_3_date",
    "email_4_sent", "email_4_date",
    "response_type", "response_date",
    "notes",
]


# ---------------------------------------------------------------------------
# Branschkategorisering
# ---------------------------------------------------------------------------

INDUSTRY_KEYWORDS = {
    "restaurang": [
        "restaurang", "restaurant", "café", "cafe", "pizzeria", "sushi",
        "thai", "bistro", "bar", "pub", "mat", "food", "kitchen", "kök",
    ],
    "frisör": [
        "frisör", "salong", "salon", "barber", "hår", "hair", "beauty",
        "skönhet", "naglar", "nails", "spa",
    ],
    "hantverkare": [
        "snickare", "elektriker", "rörmokare", "plumber", "målare", "painter",
        "bygg", "construction", "kakel", "golv", "tak", "roof", "vvs",
        "hantverkare", "craftsman", "renovering", "montör",
    ],
    "butik": [
        "butik", "shop", "retail", "affär", "handel", "store", "kiosk",
        "blomster", "present", "inredning",
    ],
    "konsult": [
        "konsult", "consultant", "rådgivare", "advisor", "coach", "byrå",
        "agency", "redovisning", "bokföring", "juridik",
    ],
    "städ": [
        "städ", "cleaning", "städfirma", "hemstäd", "kontorsstäd",
    ],
    "bilverkstad": [
        "bilverkstad", "mechanic", "auto", "bil", "car", "fordon", "däck",
    ],
}

INDUSTRY_SCORES = {
    "hantverkare": 15,
    "städ": 14,
    "restaurang": 12,
    "frisör": 11,
    "bilverkstad": 11,
    "butik": 8,
    "konsult": 7,
}

CITY_SCORES = {
    "stockholm": 10, "göteborg": 9, "malmö": 9,
    "uppsala": 8, "linköping": 8, "västerås": 8,
    "örebro": 7, "helsingborg": 7, "norrköping": 7,
    "jönköping": 7, "lund": 7, "umeå": 7,
}


# ---------------------------------------------------------------------------
# Branschklassificering
# ---------------------------------------------------------------------------

def categorize_industry(raw_industry: str) -> str:
    """Matcha rå industri-text mot en av våra branschkategorier."""
    raw = raw_industry.lower()
    for category, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if kw in raw:
                return category
    return "övrigt"


# ---------------------------------------------------------------------------
# Hemsidekontroller
# ---------------------------------------------------------------------------

def check_website_exists(url: str) -> dict:
    """Kolla om en hemsida existerar och grundläggande egenskaper."""
    if not url or url.strip() in ("", "-", "n/a"):
        return {"exists": False, "has_ssl": False, "response_time_ms": 0}

    if not url.startswith("http"):
        url = "https://" + url

    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        return {
            "exists": True,
            "has_ssl": r.url.startswith("https"),
            "response_time_ms": int(r.elapsed.total_seconds() * 1000),
        }
    except Exception:
        # Prova http om https misslyckades
        try:
            http_url = url.replace("https://", "http://")
            r = requests.get(http_url, timeout=10, allow_redirects=True)
            return {
                "exists": True,
                "has_ssl": False,
                "response_time_ms": int(r.elapsed.total_seconds() * 1000),
            }
        except Exception:
            return {"exists": False, "has_ssl": False, "response_time_ms": 0}


def check_pagespeed(url: str) -> int | None:
    """Hämta mobilpoäng från Google PageSpeed Insights API."""
    if not PAGESPEED_API_KEY or not url:
        return None

    if not url.startswith("http"):
        url = "https://" + url

    try:
        endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "key": PAGESPEED_API_KEY,
            "strategy": "mobile",
            "category": "performance",
        }
        r = requests.get(endpoint, params=params, timeout=30)
        data = r.json()
        score = data.get("lighthouseResult", {}).get("categories", {}).get(
            "performance", {}
        ).get("score")
        if score is not None:
            return int(score * 100)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Lead Scoring
# ---------------------------------------------------------------------------

def score_lead(lead: dict) -> int:
    """
    Poängsätt en lead 0-100.

    Hemsidekvalitet:  max 40p
    Verksamhet:       max 30p
    Bransch:          max 15p
    Stad:             max 10p
    Nåbarhet:         max 5p
    """
    score = 0

    # --- Hemsidekvalitet (max 40p) ---
    has_website = lead.get("has_website", "").lower() in ("true", "1", "yes", "ja")

    if not has_website:
        score += 40
    else:
        ps = lead.get("pagespeed_mobile")
        if ps and str(ps).isdigit():
            ps = int(ps)
            if ps < 30:
                score += 30
            elif ps < 50:
                score += 20
            elif ps < 70:
                score += 10

        has_ssl = lead.get("has_ssl", "").lower() in ("true", "1", "yes")
        if not has_ssl:
            score += 5

    # --- Verksamhetsviabilitet (max 30p) ---
    try:
        rating = float(lead.get("google_rating", 0) or 0)
    except (ValueError, TypeError):
        rating = 0

    if rating >= 4.0:
        score += 15
    elif rating >= 3.0:
        score += 10
    elif rating > 0:
        score += 3

    try:
        reviews = int(lead.get("review_count", 0) or 0)
    except (ValueError, TypeError):
        reviews = 0

    if reviews >= 50:
        score += 10
    elif reviews >= 20:
        score += 7
    elif reviews >= 5:
        score += 4

    if lead.get("email"):
        score += 5

    # --- Bransch (max 15p) ---
    category = lead.get("industry_category", "")
    score += INDUSTRY_SCORES.get(category, 5)

    # --- Stad (max 10p) ---
    city = (lead.get("city") or "").lower()
    city_score = 5  # default för mindre städer
    for city_name, pts in CITY_SCORES.items():
        if city_name in city:
            city_score = pts
            break
    score += city_score

    # --- Nåbarhet (max 5p) ---
    if lead.get("phone"):
        score += 3
    if lead.get("email"):
        score += 2

    return min(score, 100)


def classify_lead(score: int) -> str:
    """Klassificera en lead baserat på poäng."""
    if score >= 70:
        return "HOT"
    elif score >= 50:
        return "WARM"
    elif score >= 30:
        return "COOL"
    else:
        return "COLD"


# ---------------------------------------------------------------------------
# Deduplicering
# ---------------------------------------------------------------------------

def generate_lead_id(lead: dict) -> str:
    """Generera ett unikt lead-ID baserat på företagsnamn + stad."""
    raw = f"{lead.get('company_name', '')}-{lead.get('city', '')}".lower().strip()
    short_hash = hashlib.md5(raw.encode()).hexdigest()[:8]
    category = lead.get("industry_category", "XX")[:3].upper()
    return f"{category}-{short_hash}"


def deduplicate_leads(leads: list[dict]) -> list[dict]:
    """Ta bort duplicerade leads baserat på företagsnamn + stad."""
    seen = set()
    unique = []
    for lead in leads:
        key = (
            lead.get("company_name", "").lower().strip(),
            lead.get("city", "").lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(lead)
    dupes = len(leads) - len(unique)
    if dupes:
        print(f"  Borttagna dubletter: {dupes}")
    return unique


# ---------------------------------------------------------------------------
# Huvudprocess
# ---------------------------------------------------------------------------

def process_leads(
    input_file: Path,
    output_file: Path,
    bransch_filter: str | None = None,
    min_score: int = 0,
    check_websites: bool = False,
    dry_run: bool = False,
) -> list[dict]:
    """Läs, kvalificera, deduplicera och sortera leads."""

    # Läs CSV
    if not input_file.exists():
        print(f"Hittade inte {input_file}")
        print("Lägg din leadlista som CSV i cold-email/leads.csv")
        print("Minsta kolumner: company_name, industry, city")
        sys.exit(1)

    with open(input_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    print(f"Läste {len(leads)} leads från {input_file.name}")

    # Kontrollera kolumner
    if leads:
        missing = [c for c in REQUIRED_COLUMNS if c not in leads[0]]
        if missing:
            print(f"Saknade kolumner: {missing}")
            print(f"Tillgängliga: {list(leads[0].keys())}")
            sys.exit(1)

    # Kategorisera bransch
    for lead in leads:
        raw = lead.get("industry", "") or lead.get("category", "") or ""
        lead["industry_category"] = categorize_industry(raw)

    # Filtrera bransch
    if bransch_filter:
        leads = [l for l in leads if l["industry_category"] == bransch_filter]
        print(f"  Filtrerade till bransch '{bransch_filter}': {len(leads)} leads")

    # Deduplicera
    leads = deduplicate_leads(leads)

    # Hemsidekontroll
    if check_websites:
        print("  Kontrollerar hemsidor (detta kan ta en stund)...")
        for i, lead in enumerate(leads):
            url = lead.get("website_url") or lead.get("site") or ""
            if url and url.strip() not in ("", "-", "n/a"):
                info = check_website_exists(url)
                lead["has_website"] = str(info["exists"])
                lead["has_ssl"] = str(info["has_ssl"])

                if info["exists"] and PAGESPEED_API_KEY:
                    ps = check_pagespeed(url)
                    if ps is not None:
                        lead["pagespeed_mobile"] = str(ps)
                    time.sleep(1)  # rate limiting
            else:
                lead["has_website"] = "False"
                lead["has_ssl"] = "False"

            if (i + 1) % 10 == 0:
                print(f"    ...{i + 1}/{len(leads)} kontrollerade")

    # Generera lead-ID
    for lead in leads:
        lead["lead_id"] = generate_lead_id(lead)

    # Scoring
    for lead in leads:
        lead["lead_score"] = str(score_lead(lead))
        lead["lead_class"] = classify_lead(int(lead["lead_score"]))

    # Sätt default-status
    for lead in leads:
        if not lead.get("status"):
            lead["status"] = "NEW"
        if not lead.get("scraped_date"):
            lead["scraped_date"] = datetime.now().strftime("%Y-%m-%d")

    # Filtrera på min-score
    if min_score > 0:
        leads = [l for l in leads if int(l["lead_score"]) >= min_score]
        print(f"  Filtrerade till score >= {min_score}: {len(leads)} leads")

    # Sortera: HOT först, sedan efter score
    priority_order = {"HOT": 0, "WARM": 1, "COOL": 2, "COLD": 3}
    leads.sort(
        key=lambda l: (priority_order.get(l["lead_class"], 4), -int(l["lead_score"]))
    )

    # Statistik
    classes = {}
    for lead in leads:
        cls = lead["lead_class"]
        classes[cls] = classes.get(cls, 0) + 1

    print(f"\n  Resultat:")
    print(f"  {'='*40}")
    for cls in ["HOT", "WARM", "COOL", "COLD"]:
        count = classes.get(cls, 0)
        print(f"  {cls:6s}: {count:4d} leads")
    print(f"  {'='*40}")
    print(f"  Totalt: {len(leads)} leads")

    # Branschfördelning
    branch_counts = {}
    for lead in leads:
        cat = lead.get("industry_category", "övrigt")
        branch_counts[cat] = branch_counts.get(cat, 0) + 1

    print(f"\n  Per bransch:")
    for cat, count in sorted(branch_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:15s}: {count}")

    # Spara
    if not dry_run:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            # Använd OUTPUT_COLUMNS + ev extra kolumner från input
            all_cols = list(OUTPUT_COLUMNS)
            for lead in leads:
                for k in lead:
                    if k not in all_cols:
                        all_cols.append(k)

            writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(leads)
        print(f"\n  Sparat till {output_file}")
    else:
        print(f"\n  [DRY RUN] Inget sparat.")

    return leads


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BR Studio — Lead-processor. Kvalificerar och sorterar leads."
    )
    parser.add_argument(
        "--input", type=str, default=str(LEADS_FILE),
        help=f"Sökväg till input-CSV (default: {LEADS_FILE})",
    )
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_FILE),
        help=f"Sökväg till output-CSV (default: {OUTPUT_FILE})",
    )
    parser.add_argument(
        "--bransch",
        choices=["restaurang", "frisör", "hantverkare", "butik", "konsult", "städ", "bilverkstad"],
        default=None,
        help="Filtrera till en specifik bransch",
    )
    parser.add_argument(
        "--min-score", type=int, default=0,
        help="Visa bara leads med score >= detta värde",
    )
    parser.add_argument(
        "--check-websites", action="store_true",
        help="Kör hemsidekontroll (kräver internet, tar tid)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Visa resultat utan att spara",
    )

    args = parser.parse_args()

    process_leads(
        input_file=Path(args.input),
        output_file=Path(args.output),
        bransch_filter=args.bransch,
        min_score=args.min_score,
        check_websites=args.check_websites,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
