"""
BR Studio — Uppföljningssystem.

Skickar automatiska uppföljningar baserat på 14-dagars sekvensen:
  Dag 0:  Initial cold email (hanteras av send_emails.py)
  Dag 3:  Uppföljning 1 — ny vinkel
  Dag 7:  Uppföljning 2 — Loom-video
  Dag 10: Uppföljning 3 — social proof
  Dag 14: Breakup email

Användning:
    python scripts/send_followups.py               # skicka alla uppföljningar
    python scripts/send_followups.py --dry-run      # testa utan att skicka
    python scripts/send_followups.py --show-queue    # visa vad som väntar

Kräver i .env:
    GMAIL_ADDRESS=din@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
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

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from templates.email_templates import render_template

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

LEADS_FILE = BASE_DIR / "cold-email" / "leads_scored.csv"
SEND_LOG = BASE_DIR / "cold-email" / "send_log.csv"

STOCKHOLM_TZ = ZoneInfo("Europe/Stockholm")

# Uppföljningssekvens: status -> (dagar_efter_initial, ny_status, mejltyp, ämnesprefix)
SEQUENCE = [
    {
        "from_status": "CONTACTED",
        "to_status": "FOLLOW_UP_1",
        "days_after": 3,
        "email_type": "followup_1",
        "email_field": "email_2_sent",
        "date_field": "email_2_date",
        "check_date_field": "email_1_date",
        "subject_prefix": "Re: ",
    },
    {
        "from_status": "FOLLOW_UP_1",
        "to_status": "FOLLOW_UP_2",
        "days_after": 7,
        "email_type": "followup_2",
        "email_field": "email_3_sent",
        "date_field": "email_3_date",
        "check_date_field": "email_1_date",
        "subject_prefix": "Re: ",
    },
    {
        "from_status": "FOLLOW_UP_2",
        "to_status": "FOLLOW_UP_3",
        "days_after": 10,
        "email_type": "followup_3",
        "email_field": "email_4_sent",
        "date_field": "email_4_date",
        "check_date_field": "email_1_date",
        "subject_prefix": "Re: ",
    },
    {
        "from_status": "FOLLOW_UP_3",
        "to_status": "BREAKUP_SENT",
        "days_after": 14,
        "email_type": "breakup",
        "email_field": None,
        "date_field": None,
        "check_date_field": "email_1_date",
        "subject_prefix": "",
    },
]

# Delay mellan uppföljnings-mejl (sekunder)
FOLLOWUP_DELAY_BASE = 120
FOLLOWUP_DELAY_JITTER = 60


# ---------------------------------------------------------------------------
# Hjälpfunktioner
# ---------------------------------------------------------------------------

def read_leads() -> list[dict]:
    """Läs alla leads."""
    if not LEADS_FILE.exists():
        print(f"Hittade inte {LEADS_FILE}")
        sys.exit(1)

    with open(LEADS_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_leads(leads: list[dict]):
    """Spara alla leads tillbaka till CSV."""
    if not leads:
        return

    fieldnames = list(leads[0].keys())
    with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)


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


def send_email(to_email: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Skicka ett mejl via Gmail SMTP."""
    if dry_run:
        print(f"    [DRY RUN] -> {to_email}: {subject}")
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
        print(f"    SMTP-fel: {e}")
        return False


# ---------------------------------------------------------------------------
# Uppföljningslogik
# ---------------------------------------------------------------------------

def get_followups_due(leads: list[dict]) -> list[tuple[dict, dict]]:
    """
    Returnera leads som ska få uppföljning idag.

    Returns:
        Lista av (lead, step) tuples.
    """
    today = datetime.now(STOCKHOLM_TZ).date()
    due = []

    for lead in leads:
        # Hoppa över leads som redan svarat eller avslutats
        status = lead.get("status", "")
        if status in ("REPLIED", "MEETING_BOOKED", "PROPOSAL_SENT",
                       "WON", "LOST", "NOT_INTERESTED", "DEAD", "ARCHIVED"):
            continue

        for step in SEQUENCE:
            if lead.get("status") != step["from_status"]:
                continue

            # Kolla datum för initial email
            initial_date_str = lead.get(step["check_date_field"], "")
            if not initial_date_str:
                continue

            try:
                initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            target_date = initial_date + timedelta(days=step["days_after"])
            if target_date <= today:
                due.append((lead, step))
            break  # En lead kan bara vara i ett steg åt gången

    return due


def show_queue(leads: list[dict]):
    """Visa kommande uppföljningar."""
    today = datetime.now(STOCKHOLM_TZ).date()

    print(f"\nUppföljningskö")
    print(f"{'='*70}")
    print(f"{'Företag':<25} {'Status':<15} {'Typ':<15} {'Datum':<12}")
    print(f"{'-'*70}")

    queue_items = []
    for lead in leads:
        status = lead.get("status", "")
        if status in ("REPLIED", "WON", "LOST", "DEAD", "ARCHIVED", "NOT_INTERESTED"):
            continue

        for step in SEQUENCE:
            if lead.get("status") != step["from_status"]:
                continue

            initial_date_str = lead.get(step["check_date_field"], "")
            if not initial_date_str:
                continue

            try:
                initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            target_date = initial_date + timedelta(days=step["days_after"])
            is_due = "** IDAG **" if target_date <= today else ""
            queue_items.append((
                target_date,
                lead.get("company_name", "?"),
                step["from_status"],
                step["email_type"],
                str(target_date),
                is_due,
            ))
            break

    queue_items.sort(key=lambda x: x[0])
    for _, company, status, typ, date, due in queue_items:
        line = f"{company:<25} {status:<15} {typ:<15} {date:<12} {due}"
        print(line)

    if not queue_items:
        print("  (inga uppföljningar i kö)")

    print(f"\nTotalt i kö: {len(queue_items)}")


def run_followups(dry_run: bool = False):
    """Skicka alla uppföljningar som är redo idag."""
    leads = read_leads()
    due = get_followups_due(leads)

    print(f"BR Studio Uppföljningar")
    print(f"{'='*50}")
    print(f"Datum: {datetime.now(STOCKHOLM_TZ).strftime('%Y-%m-%d %H:%M')}")
    print(f"Uppföljningar att skicka: {len(due)}")
    if dry_run:
        print(f"LÄGE: DRY RUN")
    print(f"{'='*50}\n")

    if not due:
        print("Inga uppföljningar att skicka idag.")
        return

    sent_count = 0
    for i, (lead, step) in enumerate(due):
        bransch = lead.get("industry_category", "konsult")
        namn = lead.get("contact_name") or lead.get("company_name", "")
        företag = lead.get("company_name", "")
        stad = lead.get("city", "Stockholm")

        # Rendera uppföljningsmejl
        try:
            body = render_template(
                bransch, step["email_type"],
                namn=namn, företag=företag, stad=stad,
                bransch_specifik=lead.get("industry", bransch),
                bransch_liknande=bransch,
                loom_url="[LÄGG TILL LOOM-LÄNK]",
            )
        except (ValueError, KeyError):
            body = render_template(
                "konsult", step["email_type"] if step["email_type"] != "followup_1" else "breakup",
                namn=namn, företag=företag, stad=stad,
                bransch_specifik=bransch, bransch_liknande=bransch,
                loom_url="[LÄGG TILL LOOM-LÄNK]",
            )

        # Ämnesrad
        if step["email_type"] == "breakup":
            subject = f"Sista från mig, {namn}"
        else:
            subject = f"Re: {företag}"

        to_email = lead["email"].strip()
        print(f"[{i+1}/{len(due)}] {step['email_type']} -> {företag} ({to_email})")

        success = send_email(to_email, subject, body, dry_run=dry_run)

        if success:
            sent_count += 1
            today_str = datetime.now(STOCKHOLM_TZ).strftime("%Y-%m-%d")

            # Uppdatera lead
            lead["status"] = step["to_status"]
            if step["email_field"]:
                lead[step["email_field"]] = "True"
            if step["date_field"]:
                lead[step["date_field"]] = today_str

            if not dry_run:
                log_sent(lead, subject, step["email_type"])

            # Delay
            if i < len(due) - 1 and not dry_run:
                delay = FOLLOWUP_DELAY_BASE + random.uniform(0, FOLLOWUP_DELAY_JITTER)
                print(f"    Väntar {delay:.0f}s...")
                time.sleep(delay)

    # Markera BREAKUP_SENT som DEAD efter 7 dagar
    today = datetime.now(STOCKHOLM_TZ).date()
    dead_count = 0
    for lead in leads:
        if lead.get("status") == "BREAKUP_SENT":
            # Kolla om det gått 7 dagar sedan breakup
            initial_date_str = lead.get("email_1_date", "")
            if initial_date_str:
                try:
                    initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
                    # Breakup skickas dag 14, dead efter dag 21
                    if (today - initial_date).days >= 21:
                        lead["status"] = "DEAD"
                        dead_count += 1
                except ValueError:
                    pass

    # Spara ändringar
    if not dry_run:
        save_leads(leads)

    print(f"\n{'='*50}")
    print(f"Skickade: {sent_count}/{len(due)} uppföljningar")
    if dead_count:
        print(f"Markerade som DEAD: {dead_count}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BR Studio — Skicka uppföljningsmejl"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Visa vad som skulle skickas utan att skicka",
    )
    parser.add_argument(
        "--show-queue", action="store_true",
        help="Visa kommande uppföljningar utan att skicka",
    )

    args = parser.parse_args()

    if args.show_queue:
        leads = read_leads()
        show_queue(leads)
    else:
        run_followups(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
