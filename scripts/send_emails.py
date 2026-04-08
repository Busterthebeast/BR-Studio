"""
BR Studio — Cold email-skript.

Skickar personaliserade cold emails via Gmail SMTP med inbyggd:
- Rate limiting och randomiserade delays
- Uppvärmningsschema för nya konton
- Tidsbaserad schemaläggning (Tis-Tor, 07:30-09:30 CET)
- Batchhantering med pauser
- Dry-run-läge för testning

Användning:
    python scripts/send_emails.py                    # skicka dagens batch
    python scripts/send_emails.py --dry-run          # testa utan att skicka
    python scripts/send_emails.py --max 5            # max 5 mejl
    python scripts/send_emails.py --bransch frisör   # bara en bransch

Kräver i .env:
    GMAIL_ADDRESS=din@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    ACCOUNT_START_DATE=2026-04-08
"""

import argparse
import csv
import email.utils
import os
import random
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
except ImportError:
    print("Installera: pip install python-dotenv")
    sys.exit(1)

load_dotenv()

# Lägg till projektrot i path för template-import
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from templates.email_templates import get_random_subject, render_template

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
ACCOUNT_START_DATE = os.getenv("ACCOUNT_START_DATE", "2026-04-08")

LEADS_FILE = BASE_DIR / "cold-email" / "leads_scored.csv"
SEND_LOG = BASE_DIR / "cold-email" / "send_log.csv"

STOCKHOLM_TZ = ZoneInfo("Europe/Stockholm")

# Delay-konfiguration (sekunder)
DELAY_CONFIG = {
    "week_1":      {"base": 180, "jitter": 0.5},   # 180-270 sek
    "week_2":      {"base": 120, "jitter": 0.5},   # 120-180 sek
    "week_3":      {"base": 90,  "jitter": 0.5},   # 90-135 sek
    "established": {"base": 45,  "jitter": 0.5},   # 45-67 sek
}

BATCH_SIZE = 10          # mejl per batch
BATCH_PAUSE_BASE = 900   # 15 min paus mellan batchar (sek)

# Uppvärmningsschema: dag -> max cold emails
RAMP_UP = {
    1: 0, 2: 0, 3: 1, 4: 2, 5: 4,
    6: 0, 7: 0,  # helg
    8: 7, 9: 10, 10: 13, 11: 13, 12: 16,
    13: 0, 14: 0,  # helg
    15: 20, 16: 22, 17: 25, 18: 25, 19: 28,
    20: 0, 21: 0,  # helg
    22: 30, 23: 32, 24: 35, 25: 35, 26: 38,
    27: 0, 28: 0,  # helg
    29: 40, 30: 40,
}

MAX_DAILY_ESTABLISHED = 80

# Tillåtna skickatider (svensk tid)
SEND_WINDOWS = [
    {"days": [1, 2, 3], "start_hour": 7, "start_min": 30, "end_hour": 9, "end_min": 30},
    {"days": [1, 2, 3], "start_hour": 13, "start_min": 0, "end_hour": 14, "end_min": 30},
]


# ---------------------------------------------------------------------------
# Hjälpfunktioner
# ---------------------------------------------------------------------------

def get_account_day() -> int:
    """Hur många dagar sedan kontot startade."""
    start = datetime.strptime(ACCOUNT_START_DATE, "%Y-%m-%d").date()
    today = datetime.now(STOCKHOLM_TZ).date()
    return (today - start).days + 1


def get_daily_limit() -> int:
    """Hur många cold emails vi får skicka idag baserat på uppvärmning."""
    day = get_account_day()
    if day in RAMP_UP:
        return RAMP_UP[day]
    # Efter dag 30: gradvis ökning till max
    return min(int(40 + (day - 30) * 1.5), MAX_DAILY_ESTABLISHED)


def get_delay_config() -> dict:
    """Hämta delay-konfiguration baserat på kontots ålder."""
    day = get_account_day()
    if day <= 7:
        return DELAY_CONFIG["week_1"]
    elif day <= 14:
        return DELAY_CONFIG["week_2"]
    elif day <= 21:
        return DELAY_CONFIG["week_3"]
    else:
        return DELAY_CONFIG["established"]


def get_random_delay() -> float:
    """Beräkna randomiserad delay mellan mejl."""
    config = get_delay_config()
    base = config["base"]
    jitter = config["jitter"]
    return base + random.uniform(0, base * jitter)


def is_send_window() -> bool:
    """Kontrollera om vi är inom en tillåten skickatid."""
    now = datetime.now(STOCKHOLM_TZ)
    weekday = now.weekday()  # 0=mån, 1=tis, ...

    for window in SEND_WINDOWS:
        if weekday in window["days"]:
            start = now.replace(
                hour=window["start_hour"], minute=window["start_min"], second=0
            )
            end = now.replace(
                hour=window["end_hour"], minute=window["end_min"], second=0
            )
            if start <= now <= end:
                return True
    return False


def count_sent_today() -> int:
    """Räkna hur många mejl vi skickat idag."""
    if not SEND_LOG.exists():
        return 0

    today = datetime.now(STOCKHOLM_TZ).strftime("%Y-%m-%d")
    count = 0
    with open(SEND_LOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("date", "").startswith(today):
                count += 1
    return count


def log_sent(lead: dict, subject: str, email_type: str):
    """Logga ett skickat mejl."""
    file_exists = SEND_LOG.exists()
    with open(SEND_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date", "time", "lead_id", "company_name", "email",
            "subject", "email_type", "bransch",
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": datetime.now(STOCKHOLM_TZ).strftime("%Y-%m-%d"),
            "time": datetime.now(STOCKHOLM_TZ).strftime("%H:%M:%S"),
            "lead_id": lead.get("lead_id", ""),
            "company_name": lead.get("company_name", ""),
            "email": lead.get("email", ""),
            "subject": subject,
            "email_type": email_type,
            "bransch": lead.get("industry_category", ""),
        })


def update_lead_status(leads_file: Path, lead_id: str, updates: dict):
    """Uppdatera en lead i CSV-filen."""
    rows = []
    with open(leads_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get("lead_id") == lead_id:
                row.update(updates)
            rows.append(row)

    with open(leads_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Mejl-sändning
# ---------------------------------------------------------------------------

def send_email(to_email: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Skicka ett mejl via Gmail SMTP."""
    if dry_run:
        print(f"  [DRY RUN] Till: {to_email}")
        print(f"  Ämne: {subject}")
        print(f"  ---")
        print(f"  {body[:200]}...")
        print()
        return True

    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("  FEL: GMAIL_ADDRESS och GMAIL_APP_PASSWORD måste sättas i .env")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="gmail.com")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except smtplib.SMTPException as e:
        print(f"  SMTP-fel: {e}")
        return False


# ---------------------------------------------------------------------------
# Huvudlogik
# ---------------------------------------------------------------------------

def get_sendable_leads(bransch_filter: str | None = None) -> list[dict]:
    """Hämta leads som ska få initial cold email (status=NEW, har email)."""
    if not LEADS_FILE.exists():
        print(f"Hittade inte {LEADS_FILE}")
        print("Kör först: python scripts/process_leads.py")
        sys.exit(1)

    with open(LEADS_FILE, newline="", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    # Filtrera: bara NEW-leads med email och minst COOL score
    sendable = [
        l for l in leads
        if l.get("status", "NEW") == "NEW"
        and l.get("email", "").strip()
        and l.get("lead_class") in ("HOT", "WARM", "COOL")
    ]

    if bransch_filter:
        sendable = [l for l in sendable if l.get("industry_category") == bransch_filter]

    # Sortera: HOT först
    priority = {"HOT": 0, "WARM": 1, "COOL": 2}
    sendable.sort(key=lambda l: (priority.get(l.get("lead_class", "COOL"), 3), -int(l.get("lead_score", 0))))

    return sendable


def run_send(
    max_emails: int | None = None,
    bransch_filter: str | None = None,
    dry_run: bool = False,
    force_time: bool = False,
):
    """Kör dagens mejlutskick."""

    # Kontrollera tidsfönster
    if not force_time and not dry_run and not is_send_window():
        now = datetime.now(STOCKHOLM_TZ)
        print(f"Utanför skickatid (nu: {now.strftime('%A %H:%M')} CET)")
        print("Tillåtna tider: Tis-Tor 07:30-09:30, 13:00-14:30")
        print("Använd --force-time för att ignorera tidsfönstret")
        return

    # Kontrollera daglig gräns
    daily_limit = get_daily_limit()
    sent_today = count_sent_today()
    remaining = daily_limit - sent_today
    account_day = get_account_day()

    print(f"BR Studio Cold Email")
    print(f"{'='*50}")
    print(f"Kontodag: {account_day}")
    print(f"Daglig gräns: {daily_limit} mejl")
    print(f"Redan skickat idag: {sent_today}")
    print(f"Kvar att skicka: {remaining}")
    print(f"Delay: {get_delay_config()['base']}s (+ jitter)")
    if dry_run:
        print(f"LÄGE: DRY RUN (skickar inte)")
    print(f"{'='*50}\n")

    if remaining <= 0 and not dry_run:
        print("Daglig gräns nådd. Försök igen imorgon.")
        return

    # Hämta leads
    leads = get_sendable_leads(bransch_filter)
    if not leads:
        print("Inga leads att skicka till.")
        print("  - Har du kört process_leads.py?")
        print("  - Finns det leads med status=NEW och email?")
        return

    # Begränsa antal
    to_send = min(remaining, len(leads))
    if max_emails:
        to_send = min(to_send, max_emails)

    print(f"Skickar till {to_send} leads (av {len(leads)} tillgängliga)\n")

    sent_count = 0
    for i, lead in enumerate(leads[:to_send]):
        bransch = lead.get("industry_category", "konsult")
        namn = lead.get("contact_name") or lead.get("company_name", "")
        företag = lead.get("company_name", "")
        stad = lead.get("city", "Stockholm")
        bransch_specifik = lead.get("industry", bransch)

        # Välj ämnesrad
        subject = get_random_subject(bransch)
        try:
            subject = subject.format(
                namn=namn, företag=företag, stad=stad,
                bransch_specifik=bransch_specifik,
            )
        except KeyError:
            pass

        # Rendera mejl
        try:
            body = render_template(
                bransch, "initial",
                namn=namn, företag=företag, stad=stad,
                bransch_specifik=bransch_specifik,
                bransch_liknande=bransch,
            )
        except ValueError:
            # Fallback till konsult-mall
            body = render_template(
                "konsult", "initial",
                namn=namn, företag=företag, stad=stad,
            )

        # Skicka
        to_email = lead["email"].strip()
        print(f"[{i+1}/{to_send}] {företag} ({bransch}) -> {to_email}")

        success = send_email(to_email, subject, body, dry_run=dry_run)

        if success:
            sent_count += 1
            today = datetime.now(STOCKHOLM_TZ).strftime("%Y-%m-%d")

            if not dry_run:
                log_sent(lead, subject, "initial")
                update_lead_status(LEADS_FILE, lead["lead_id"], {
                    "status": "CONTACTED",
                    "email_1_sent": "True",
                    "email_1_date": today,
                })

            # Delay före nästa mejl (inte efter sista)
            if i < to_send - 1:
                delay = get_random_delay()

                # Batchpaus var BATCH_SIZE:e mejl
                if (i + 1) % BATCH_SIZE == 0:
                    delay = BATCH_PAUSE_BASE + random.uniform(0, 300)
                    print(f"  Batchpaus: {delay:.0f}s")
                else:
                    if not dry_run:
                        print(f"  Väntar {delay:.0f}s...")

                if not dry_run:
                    time.sleep(delay)
        else:
            print(f"  Misslyckades att skicka till {to_email}")

    print(f"\n{'='*50}")
    print(f"Klart! Skickade: {sent_count}/{to_send}")
    print(f"Totalt idag: {sent_today + sent_count}/{daily_limit}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BR Studio — Skicka cold emails med Gmail SMTP"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Visa vad som skulle skickas utan att faktiskt skicka",
    )
    parser.add_argument(
        "--max", type=int, default=None,
        help="Max antal mejl att skicka",
    )
    parser.add_argument(
        "--bransch",
        choices=["restaurang", "frisör", "hantverkare", "butik", "konsult"],
        default=None,
        help="Skicka bara till en specifik bransch",
    )
    parser.add_argument(
        "--force-time", action="store_true",
        help="Ignorera tidsfönster-begränsning",
    )

    args = parser.parse_args()

    run_send(
        max_emails=args.max,
        bransch_filter=args.bransch,
        dry_run=args.dry_run,
        force_time=args.force_time,
    )


if __name__ == "__main__":
    main()
