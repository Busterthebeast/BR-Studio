"""
BR Studio — Dashboard.

Visar statistik över outreach-pipeline:
skickade, svar, svarsfrekvens, uppföljningar, pipeline-status.

Användning:
    python scripts/dashboard.py              # komplett dashboard
    python scripts/dashboard.py --today      # bara dagens stats
    python scripts/dashboard.py --pipeline   # bara pipeline-status

"""

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent
LEADS_FILE = BASE_DIR / "cold-email" / "leads_scored.csv"
SEND_LOG = BASE_DIR / "cold-email" / "send_log.csv"

STOCKHOLM_TZ = ZoneInfo("Europe/Stockholm")


# ---------------------------------------------------------------------------
# Data-läsning
# ---------------------------------------------------------------------------

def read_leads() -> list[dict]:
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_send_log() -> list[dict]:
    if not SEND_LOG.exists():
        return []
    with open(SEND_LOG, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Dashboard-komponenter
# ---------------------------------------------------------------------------

def show_header():
    now = datetime.now(STOCKHOLM_TZ)
    print()
    print("=" * 60)
    print("  BR STUDIO — OUTREACH DASHBOARD")
    print(f"  {now.strftime('%Y-%m-%d %H:%M')} CET")
    print("=" * 60)


def show_pipeline(leads: list[dict]):
    """Visa pipeline-status."""
    print("\n  PIPELINE")
    print("  " + "-" * 50)

    status_counts = Counter(l.get("status", "UNKNOWN") for l in leads)

    # Ordning som matchar pipeline-flödet
    status_order = [
        "NEW", "CONTACTED", "FOLLOW_UP_1", "FOLLOW_UP_2",
        "FOLLOW_UP_3", "BREAKUP_SENT",
        "REPLIED", "MEETING_BOOKED", "PROPOSAL_SENT",
        "WON", "LOST", "NOT_INTERESTED", "DEAD", "ARCHIVED",
    ]

    total = len(leads)
    for status in status_order:
        count = status_counts.get(status, 0)
        if count > 0:
            pct = (count / total * 100) if total else 0
            bar = "#" * int(pct / 2)
            print(f"  {status:<18} {count:>4}  {pct:5.1f}%  {bar}")

    # Visa okända statusar
    for status, count in sorted(status_counts.items()):
        if status not in status_order and count > 0:
            pct = (count / total * 100) if total else 0
            print(f"  {status:<18} {count:>4}  {pct:5.1f}%")

    print(f"  {'':18} {'----':>4}")
    print(f"  {'TOTALT':<18} {total:>4}")


def show_email_stats(leads: list[dict], send_log: list[dict]):
    """Visa mejlstatistik."""
    print("\n  MEJLSTATISTIK")
    print("  " + "-" * 50)

    # Räkna skickade per typ
    type_counts = Counter(r.get("email_type", "?") for r in send_log)
    total_sent = len(send_log)

    print(f"  Totalt skickade mejl:  {total_sent}")
    for typ in ["initial", "followup_1", "followup_2", "followup_3", "breakup"]:
        count = type_counts.get(typ, 0)
        print(f"    {typ:<20} {count:>4}")

    # Svarsfrekvens
    replied = sum(1 for l in leads if l.get("status") in (
        "REPLIED", "MEETING_BOOKED", "PROPOSAL_SENT", "WON", "LOST"
    ))
    contacted = sum(1 for l in leads if l.get("status") not in ("NEW", ""))
    reply_rate = (replied / contacted * 100) if contacted else 0

    print(f"\n  Kontaktade leads:      {contacted}")
    print(f"  Svar:                  {replied}")
    print(f"  Svarsfrekvens:         {reply_rate:.1f}%")


def show_bransch_stats(leads: list[dict]):
    """Visa statistik per bransch."""
    print("\n  PER BRANSCH")
    print("  " + "-" * 50)
    print(f"  {'Bransch':<15} {'Total':>6} {'HOT':>5} {'WARM':>5} {'Kontaktad':>10} {'Svar':>5}")
    print(f"  {'':15} {'-----':>6} {'----':>5} {'----':>5} {'---------':>10} {'----':>5}")

    branches = Counter(l.get("industry_category", "övrigt") for l in leads)

    for branch in sorted(branches.keys()):
        branch_leads = [l for l in leads if l.get("industry_category") == branch]
        total = len(branch_leads)
        hot = sum(1 for l in branch_leads if l.get("lead_class") == "HOT")
        warm = sum(1 for l in branch_leads if l.get("lead_class") == "WARM")
        contacted = sum(1 for l in branch_leads if l.get("status") not in ("NEW", ""))
        replied = sum(1 for l in branch_leads if l.get("status") in (
            "REPLIED", "MEETING_BOOKED", "PROPOSAL_SENT", "WON"
        ))
        print(f"  {branch:<15} {total:>6} {hot:>5} {warm:>5} {contacted:>10} {replied:>5}")


def show_today_stats(send_log: list[dict]):
    """Visa dagens aktivitet."""
    today_str = datetime.now(STOCKHOLM_TZ).strftime("%Y-%m-%d")

    today_sent = [r for r in send_log if r.get("date") == today_str]

    print(f"\n  IDAG ({today_str})")
    print("  " + "-" * 50)
    print(f"  Mejl skickade idag:    {len(today_sent)}")

    if today_sent:
        type_counts = Counter(r.get("email_type", "?") for r in today_sent)
        for typ, count in sorted(type_counts.items()):
            print(f"    {typ:<20} {count:>4}")

        # Senast skickade
        last = today_sent[-1]
        print(f"\n  Senast skickad:")
        print(f"    {last.get('time', '?')} -> {last.get('company_name', '?')} ({last.get('email_type', '?')})")


def show_revenue(leads: list[dict]):
    """Visa intäktsöversikt."""
    print("\n  INTÄKTER")
    print("  " + "-" * 50)

    won = [l for l in leads if l.get("status") == "WON"]
    pipeline = [l for l in leads if l.get("status") in (
        "REPLIED", "MEETING_BOOKED", "PROPOSAL_SENT"
    )]

    print(f"  Stängda deals:         {len(won)}")
    print(f"  I pipeline:            {len(pipeline)}")
    print(f"    - Svar mottagna:     {sum(1 for l in pipeline if l.get('status') == 'REPLIED')}")
    print(f"    - Möten bokade:      {sum(1 for l in pipeline if l.get('status') == 'MEETING_BOOKED')}")
    print(f"    - Offerter skickade: {sum(1 for l in pipeline if l.get('status') == 'PROPOSAL_SENT')}")


def show_upcoming_followups(leads: list[dict]):
    """Visa uppföljningar som ska skickas snart."""
    from datetime import timedelta

    today = datetime.now(STOCKHOLM_TZ).date()

    FOLLOWUP_DAYS = {
        "CONTACTED": 3,
        "FOLLOW_UP_1": 7,
        "FOLLOW_UP_2": 10,
        "FOLLOW_UP_3": 14,
    }

    print("\n  UPPFOLJNINGAR (kommande 7 dagar)")
    print("  " + "-" * 50)

    upcoming = []
    for lead in leads:
        status = lead.get("status", "")
        if status not in FOLLOWUP_DAYS:
            continue

        initial_date_str = lead.get("email_1_date", "")
        if not initial_date_str:
            continue

        try:
            initial_date = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        target_date = initial_date + timedelta(days=FOLLOWUP_DAYS[status])
        days_until = (target_date - today).days

        if -3 <= days_until <= 7:  # inkludera försenade
            upcoming.append({
                "company": lead.get("company_name", "?"),
                "type": status,
                "date": target_date,
                "days_until": days_until,
            })

    upcoming.sort(key=lambda x: x["date"])

    if upcoming:
        for item in upcoming:
            marker = "** IDAG **" if item["days_until"] == 0 else (
                f"FÖRSENAD ({-item['days_until']}d)" if item["days_until"] < 0 else
                f"om {item['days_until']}d"
            )
            print(f"  {item['date']}  {item['company']:<20} {item['type']:<15} {marker}")
    else:
        print("  (inga uppföljningar kommande 7 dagar)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BR Studio — Outreach Dashboard"
    )
    parser.add_argument("--today", action="store_true", help="Visa bara dagens stats")
    parser.add_argument("--pipeline", action="store_true", help="Visa bara pipeline")

    args = parser.parse_args()

    leads = read_leads()
    send_log = read_send_log()

    show_header()

    if not leads and not send_log:
        print("\n  Ingen data ännu.")
        print("  1. Kör: python scripts/process_leads.py")
        print("  2. Kör: python scripts/send_emails.py --dry-run")
        print()
        return

    if args.today:
        show_today_stats(send_log)
    elif args.pipeline:
        show_pipeline(leads)
    else:
        show_pipeline(leads)
        show_email_stats(leads, send_log)
        show_bransch_stats(leads)
        show_today_stats(send_log)
        show_upcoming_followups(leads)
        show_revenue(leads)

    print()


if __name__ == "__main__":
    main()
