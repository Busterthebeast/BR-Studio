"""
BR Studio — Mejlmallar för cold outreach.

5 branscher x (1 initial + 3 uppföljningar) = 20 mallar.
Alla texter på svenska, 50-120 ord, optimerade för Gmail deliverability.

Användning:
    from templates.email_templates import get_template, get_subject_lines

    template = get_template("restaurang", "initial")
    subject = get_subject_lines("restaurang")
"""

import random


# ---------------------------------------------------------------------------
# Ämnesrader per bransch (3 varianter som roteras)
# ---------------------------------------------------------------------------

SUBJECT_LINES = {
    "restaurang": [
        "Såg er meny online, {namn}",
        "{företag} — en observation om er hemsida",
        "Snabb fråga om {företag}s online-närvaro",
    ],
    "frisör": [
        "Hittade {företag} på Google, {namn}",
        "{företag} — syns ni online?",
        "Snabb fråga, {namn}",
    ],
    "hantverkare": [
        "Sökte {bransch_specifik} i {stad} — hittade {företag}",
        "{företag} — en tanke om er hemsida",
        "Snabb fråga om {företag}s synlighet online",
    ],
    "butik": [
        "Hittade {företag} i {stad}, {namn}",
        "{företag} — en observation",
        "Snabb fråga om {företag}s hemsida",
    ],
    "konsult": [
        "Såg din profil, {namn}",
        "{företag} — en tanke om er webb",
        "Hej {namn} — snabb fråga",
    ],
}

# ---------------------------------------------------------------------------
# Initiala cold emails (dag 0)
# ---------------------------------------------------------------------------

INITIAL_TEMPLATES = {
    "restaurang": (
        "Hej {namn},\n\n"
        "Kollade precis på {företag} online och såg att er meny inte riktigt "
        "kommer till sin rätt på mobilen. Många av era kunder googlar nog "
        '"{företag}" innan de bokar — och första intrycket online spelar roll.\n\n'
        "Jag bygger hemsidor för restauranger i {stad} och fixade nyligen en "
        "liknande sida åt ett annat ställe här. Skulle det vara intressant att "
        "se hur {företag}s hemsida skulle kunna se ut?\n\n"
        "Ingen förpliktelse alls.\n\n"
        "/Buster"
    ),
    "frisör": (
        "Hej {namn},\n\n"
        'Jag sökte "frisör {stad}" på Google och hittade {företag} — men er '
        "hemsida gör inte rättvisa åt det ni verkar leverera baserat på era "
        "recensioner.\n\n"
        "Jag hjälper salonger i {stad} med moderna hemsidor som gör det enkelt "
        "att boka online och synas bättre på Google. Kan jag visa dig ett "
        "gratis förslag på hur det skulle kunna se ut för {företag}?\n\n"
        "Ingen press.\n\n"
        "/Buster"
    ),
    "hantverkare": (
        "Hej {namn},\n\n"
        'Sökte "{bransch_specifik} {stad}" på Google och hittade {företag}. '
        "Er verksamhet ser stabil ut baserat på recensionerna, men hemsidan "
        "matchar inte riktigt kvaliteten ni levererar.\n\n"
        "Jag bygger hemsidor åt hantverksföretag och vet att de flesta kunder "
        "googlar innan de ringer — en bra hemsida gör stor skillnad. Vill du "
        "se ett kort förslag på hur {företag}s sida skulle kunna se ut?\n\n"
        "Helt gratis, ingen hake.\n\n"
        "/Buster"
    ),
    "butik": (
        "Hej {namn},\n\n"
        "Hittade {företag} i {stad} och kollade på er hemsida. De flesta "
        "kunder googlar innan de besöker en butik — och just nu missar ni "
        "nog en del besökare som inte hittar er online.\n\n"
        "Jag bygger hemsidor för butiker i {stad} och skulle gärna visa dig "
        "hur en uppdaterad sida för {företag} skulle kunna se ut.\n\n"
        "Intresserad?\n\n"
        "/Buster"
    ),
    "konsult": (
        "Hej {namn},\n\n"
        "Såg din profil och att du driver {företag}. Många konsulter jag "
        "pratar med säger att potentiella kunder kollar hemsidan innan de "
        "hör av sig — och att det spelar roll vilket intryck den ger.\n\n"
        "Jag bygger professionella hemsidor för konsulter och småföretag. "
        "Kan jag visa dig ett gratis förslag på hur en hemsida för {företag} "
        "skulle kunna se ut?\n\n"
        "Ingen förpliktelse.\n\n"
        "/Buster"
    ),
}

# ---------------------------------------------------------------------------
# Uppföljning 1 — dag 3 (ny vinkel, 50-75 ord)
# ---------------------------------------------------------------------------

FOLLOWUP_1_TEMPLATES = {
    "restaurang": (
        "Hej igen {namn},\n\n"
        "Ville bara nämna — jag kollade på andra restauranger i {stad} och "
        "de flesta som syns högt på Google har en mobilanpassad hemsida med "
        "meny och enkel bordsbokning.\n\n"
        "Tror att {företag} skulle ha nytta av det. Vill du se ett förslag?\n\n"
        "/Buster"
    ),
    "frisör": (
        "Hej igen {namn},\n\n"
        "Noterade att flera salonger i {stad} nu har hemsidor med direkt "
        "onlinebokning — det verkar driva en hel del nya kunder dit.\n\n"
        "Har ni funderat på det för {företag}?\n\n"
        "/Buster"
    ),
    "hantverkare": (
        "Hej igen {namn},\n\n"
        "De flesta som söker {bransch_specifik} i {stad} jämför 3–4 företag "
        "online innan de ringer. En tydlig hemsida med bilder på tidigare "
        "jobb gör ofta skillnaden.\n\n"
        "Är det något ni tänkt på för {företag}?\n\n"
        "/Buster"
    ),
    "butik": (
        "Hej igen {namn},\n\n"
        "Kollade på butiker i {stad} och märkte att de som syns bäst online "
        "ofta har en enkel, snygg hemsida — inte nödvändigtvis en webbshop, "
        "utan bara en sida som visar vad ni erbjuder.\n\n"
        "Vore det intressant för {företag}?\n\n"
        "/Buster"
    ),
    "konsult": (
        "Hej igen {namn},\n\n"
        "Funderade vidare — en sak jag märkt är att konsulter med en "
        "professionell hemsida ofta får mer trovärdighet hos potentiella "
        "kunder som hittar dem via LinkedIn.\n\n"
        "Är det något du tänkt på?\n\n"
        "/Buster"
    ),
}

# ---------------------------------------------------------------------------
# Uppföljning 2 — dag 7 (social proof + Loom-referens)
# ---------------------------------------------------------------------------

FOLLOWUP_2_TEMPLATES = {
    "_generic": (
        "Hej {namn},\n\n"
        "Jag spelade in en kort video (90 sek) där jag visar hur {företag}s "
        "online-närvaro ser ut idag och vad jag skulle förändra.\n\n"
        "Ingen förpliktelse — ta en titt när du har en minut: {loom_url}\n\n"
        "/Buster"
    ),
}

# ---------------------------------------------------------------------------
# Uppföljning 3 — dag 10 (social proof utan Loom)
# ---------------------------------------------------------------------------

FOLLOWUP_3_TEMPLATES = {
    "_generic": (
        "Hej {namn},\n\n"
        "Tänkte att detta kanske är relevant: jag byggde nyligen en hemsida "
        "åt ett {bransch_liknande}-företag i Stockholm. Resultatet: fler "
        "besökare från Google och deras första förfrågan via hemsidan kom "
        "inom en vecka.\n\n"
        "Om du är nyfiken kan jag visa hur det skulle se ut för {företag}.\n\n"
        "/Buster"
    ),
}

# ---------------------------------------------------------------------------
# Breakup email — dag 14 (sista mejlet)
# ---------------------------------------------------------------------------

BREAKUP_TEMPLATES = {
    "_generic": (
        "Hej {namn},\n\n"
        "Jag har hört av mig några gånger nu och förstår att timing kanske "
        "inte är rätt. Jag vill inte vara den som spammar, så detta är mitt "
        "sista mejl.\n\n"
        "Om du någon gång i framtiden vill prata hemsidor — svara bara på "
        "detta mejl så finns jag här.\n\n"
        "Lycka till med allt!\n\n"
        "/Buster"
    ),
}

# ---------------------------------------------------------------------------
# LinkedIn-mallar
# ---------------------------------------------------------------------------

LINKEDIN_CONNECTION_NOTE = (
    "Hej {namn}! Såg att du driver {företag} — vore kul att koppla ihop. "
    "Jobbar själv med webb för lokala företag här i Sverige."
)

LINKEDIN_MESSAGE_1 = (
    "Tack för att du accepterade, {namn}!\n\n"
    "Jag hjälpte nyligen ett {bransch_liknande}-företag i {stad} med en ny "
    "hemsida — de fick fler förfrågningar via Google redan första månaden.\n\n"
    "Jag kollade på {företag}s hemsida och såg några saker som jag tror "
    "skulle kunna göra stor skillnad. Skulle du vara öppen för att jag "
    "skickar över ett kort, gratis förslag?\n\n"
    "Ingen press alls!\n\n"
    "/Buster"
)

LINKEDIN_MESSAGE_2 = (
    "Hej igen {namn}!\n\n"
    "Ville bara följa upp kort — jag vet att det är mycket som händer "
    "i vardagen när man driver företag.\n\n"
    "Om tajmingen är bättre längre fram så finns jag här. "
    "Önskar dig en bra vecka!\n\n"
    "/Buster"
)


# ---------------------------------------------------------------------------
# Publikt API
# ---------------------------------------------------------------------------

def get_subject_lines(bransch: str) -> list[str]:
    """Returnera lista med ämnesrads-varianter för en bransch."""
    return SUBJECT_LINES.get(bransch, SUBJECT_LINES["konsult"])


def get_random_subject(bransch: str) -> str:
    """Returnera en slumpmässig ämnesrad för en bransch."""
    return random.choice(get_subject_lines(bransch))


def get_template(bransch: str, typ: str) -> str:
    """
    Hämta en mejlmall.

    Args:
        bransch: "restaurang", "frisör", "hantverkare", "butik", "konsult"
        typ: "initial", "followup_1", "followup_2", "followup_3", "breakup"

    Returns:
        Malltext med {platshållare} för personalisering.
    """
    templates = {
        "initial": INITIAL_TEMPLATES,
        "followup_1": FOLLOWUP_1_TEMPLATES,
        "followup_2": FOLLOWUP_2_TEMPLATES,
        "followup_3": FOLLOWUP_3_TEMPLATES,
        "breakup": BREAKUP_TEMPLATES,
    }

    template_group = templates.get(typ)
    if template_group is None:
        raise ValueError(f"Okänd mejltyp: {typ}. Välj: {list(templates.keys())}")

    # Branschspecifik mall, eller generisk (_generic) som fallback
    return template_group.get(bransch, template_group.get("_generic", ""))


def render_template(bransch: str, typ: str, **kwargs) -> str:
    """
    Hämta och fyll i en mejlmall med konkreta värden.

    Exempel:
        render_template("restaurang", "initial",
                        namn="Anna", företag="Café Luna",
                        stad="Stockholm")
    """
    template = get_template(bransch, typ)
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(
            f"Saknar platshållare {e} för bransch={bransch}, typ={typ}. "
            f"Skicka med: {e.args[0]}=..."
        )


# ---------------------------------------------------------------------------
# CLI — visa alla mallar
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="BR Studio mejlmallar — visa och testa mallar"
    )
    parser.add_argument(
        "--bransch",
        choices=["restaurang", "frisör", "hantverkare", "butik", "konsult", "alla"],
        default="alla",
        help="Vilken bransch att visa mallar för",
    )
    parser.add_argument(
        "--typ",
        choices=["initial", "followup_1", "followup_2", "followup_3", "breakup", "alla"],
        default="alla",
        help="Vilken mejltyp att visa",
    )
    args = parser.parse_args()

    branscher = (
        ["restaurang", "frisör", "hantverkare", "butik", "konsult"]
        if args.bransch == "alla"
        else [args.bransch]
    )
    typer = (
        ["initial", "followup_1", "followup_2", "followup_3", "breakup"]
        if args.typ == "alla"
        else [args.typ]
    )

    # Exempeldata för rendering
    example_data = {
        "namn": "Anna",
        "företag": "Exempelföretaget",
        "stad": "Stockholm",
        "bransch_specifik": "snickare",
        "bransch_liknande": "hantverks",
        "loom_url": "https://loom.com/share/exempel",
    }

    for bransch in branscher:
        print(f"\n{'='*60}")
        print(f"BRANSCH: {bransch.upper()}")
        print(f"{'='*60}")

        print(f"\nÄmnesrader:")
        for s in get_subject_lines(bransch):
            print(f"  - {s}")

        for typ in typer:
            template = get_template(bransch, typ)
            if template:
                print(f"\n--- {typ.upper()} ---")
                try:
                    print(template.format(**example_data))
                except KeyError:
                    print(template)
