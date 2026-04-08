# Hemsida-Byrå Masterplan V3
### Datadriven plan — från research till första kunden

> **Kärnidé:** Bygg och sälj hemsidor till svenska småföretag.
> När kunden litar på dig, lägg på AI-tjänster som tillägg.
> **Mål:** Första betalningen inom 2 veckor. 10 000–20 000 kr/mån inom 90 dagar.
> **Startkostnad:** 0 kr.
> **Baserad på:** Deep research av deliverability, copywriting, LinkedIn, lead-kvalificering, uppföljningssekvenser och Framer-workflow (april 2026).

---

## DEL 1 — VAD DU SÄLJER

### Steg 1 — Kärnprodukt: Hemsidor

| Paket | Pris | Innehåll | Tid |
|-------|------|----------|-----|
| **Bas** | 4 000–6 000 kr | 1–3 sidor, mobilanpassad, kontaktformulär, grund-SEO | ~3h |
| **Standard** | 7 000–10 000 kr | 4–6 sidor, animationer, Analytics, GSC, schema markup, 2 revisioner | ~5h |
| **Premium** | 12 000–18 000 kr | 7+ sidor, CMS, chatbot, bokningssystem, avancerad SEO, Loom-guide | ~8h |

### Steg 2 — Tillägg (efter leverans)
- AI-chatbot på hemsidan (+2 000 kr)
- SEO-artiklar varje månad (+2 000 kr/mån)
- Automatiserade mejlsekvenser (+1 500 kr)

### Steg 3 — Retainer
- Underhållsavtal: 500–1 500 kr/mån

---

## DEL 2 — VERKTYG (alla gratis i fas 1)

| Verktyg | Syfte | Kostnad |
|---------|-------|---------|
| Apollo.io | Hitta och scrapa leads + kontaktinfo | Free tier (250 mejl/dag) |
| Waalaxy | LinkedIn-automation | 80 requests/mån gratis |
| Gmail + Python SMTP | Cold email | 0 kr |
| Framer | Bygga hemsidor | 0 kr (kunden betalar hosting ~105 kr/mån) |
| Chatbase | AI-chatbot upsell | Free tier |
| Loom | Personliga videos i outreach | 0 kr |
| Google Sheets | CRM/pipeline | 0 kr |
| Carrd | Egen portföljsida | 0 kr |

---

## DEL 3 — LEAD GENERATION

### Målgrupp (prioriterat)
Branscher rankade efter lägst digital mognad i Sverige:

| Prioritet | Bransch | Varför |
|-----------|---------|--------|
| 1 | **Bygg & Hantverk** | Lägst digitala mognad bland svenska SMB |
| 2 | **Städfirmor** | Många mikrofirmor utan hemsida |
| 3 | **Restauranger** | Förlitar sig på Google Maps, hemsida ofta föråldrad |
| 4 | **Frisörer & Salong** | Instagram-fokuserade, hemsida saknas eller är gammal |
| 5 | **Butiker & Konsulter** | Varierande, selektiv targeting |

### Lead Scraping med Apollo.io
```
Sökfilter per bransch:
- Industry: Construction / Restaurants / Beauty / Retail / Consulting
- Location: Stockholm / Göteborg / Malmö / Uppsala
- Company Size: 1-10 anställda
- Country: Sweden
```
- Scrapa 50–80 leads per bransch
- Totalt: 300–400 leads i vecka 1
- Kostnad: 0 kr (Apollo free tier)

### Lead-kvalificering (automatiserad)
Varje lead får en score 0–100 baserad på:
- **Hemsidekvalitet (40p):** Ingen hemsida = 40p, PageSpeed < 30 = 30p, < 50 = 20p
- **Verksamhetsviabilitet (30p):** Google-betyg 4.0+ = 15p, 50+ recensioner = 10p, nåbar via mejl = 5p
- **Bransch (15p):** Bygg = 15p, Restaurang = 12p, Frisör = 11p, Butik = 8p
- **Stad (10p):** Stockholm = 10p, Göteborg/Malmö = 9p, övriga = 5–8p
- **Nåbarhet (5p):** Har telefon = 3p, har mejl = 2p

Klassificering:
- **HOT (70+):** Kontakta omedelbart
- **WARM (50–69):** Kontakta i batch 2
- **COOL (30–49):** Kontakta om kapacitet finns
- **COLD (<30):** Hoppa över

---

## DEL 4 — OUTREACH-SYSTEMET

### Gmail SMTP — Tekniska regler

| Parameter | Värde |
|-----------|-------|
| Max dagligt (nytt konto) | 5 mejl |
| Max dagligt (vecka 1) | 10 mejl |
| Max dagligt (månad 1) | 40 mejl |
| Max dagligt (etablerat) | 80 mejl |
| Delay mellan mejl | 90–135 sek (randomiserat) |
| Batchpaus | 15 min var 10:e mejl |
| Skickatider | Tis–Tor, 07:30–09:30 + 13:00–14:30 CET |
| Format | Ren text, inga bilder/HTML |
| Max länkar | 1 (helst 0 i första mejlet) |
| Max ord | 50–120 per mejl |

### Uppvärmningsschema för nytt Gmail-konto

| Period | Daglig volym | Mix |
|--------|-------------|-----|
| Dag 1–3 | 3–5 | Bara personliga mejl |
| Dag 4–7 | 5–10 | Personliga + 2–3 cold |
| Vecka 2 | 10–15 | 5 personliga + 10 cold |
| Vecka 3 | 15–25 | Mest cold |
| Vecka 4 | 25–40 | Full cold outreach |
| Månad 2 | 40–60 | Max kapacitet |
| Månad 3+ | 60–80 | Hållbar max |

### Mejlmallsstrategi
- **5 branschspecifika mallar** med personalisering per lead
- **3 ämnesrads-varianter** per bransch (roteras)
- **4 mejltyper:** Initial, uppföljning 1, uppföljning 2 (Loom), breakup
- **Kulturanpassat:** Du-tilltal, inget tryck, rak kommunikation
- **CTA:** "Kan jag visa ett gratis förslag?" (intressebaserad, inte boknings-CTA)
- **Spamundvikande:** Inga trigger-ord (gratis, erbjudande, rabatt), variation i varje mejl

### 14-dagars Multi-Channel Sekvens

| Dag | Kanal | Åtgärd |
|-----|-------|--------|
| 0 (Tis) | **Mejl** | Initial cold email — personaliserad observation |
| 1 (Ons) | **LinkedIn** | Connection request med kort note |
| 3 (Fre) | **Mejl** | Uppföljning 1 — ny vinkel, 50–75 ord |
| 5 | **LinkedIn** | Meddelande (om accepted) |
| 7 (Tis) | **Mejl + Loom** | 60–90 sek video som visar deras hemsida + förbättringsförslag |
| 10 (Fre) | **Mejl** | Social proof — mini case study |
| 14 (Tis) | **Mejl** | Breakup email — "sista från mig" |

**Förväntade resultat per 50 leads:**
- Öppningsfrekvens: 50–60%
- Loom-visningar: 15–25%
- Svar: 4–7 (8–15%)
- Möten: 1–3
- Stängda deals: 1

### LinkedIn med Waalaxy

| Parameter | Värde |
|-----------|-------|
| Dagliga requests | Max 3 |
| Månatliga requests | Max 80 |
| Aktiva timmar | 08:00–10:30 CET |
| Sekvens | "Invitation + 2 Messages" |
| Delay efter accept | 1 dag |
| Delay mellan meddelanden | 4 dagar |

---

## DEL 5 — DAGSCHEMA

**Onsdag (dag 1):** Skapa Gmail-konto för outreach, uppdatera LinkedIn-profil
**Torsdag:** Scrapa 200+ leads med Apollo.io, kör process_leads.py
**Fredag:** Bygg alla Python-skript klart, testa dry-run
**Lördag:** Sätt upp Gmail app-lösenord, bygg landningssida, Waalaxy-setup
**Söndag:** Go live — kör första 5–10 mejlen (uppvärmning)

**Varje arbetsdag (15 min, 07:30):**
```bash
python scripts/send_emails.py          # skickar dagens batch
python scripts/send_followups.py       # skickar uppföljningar
python scripts/dashboard.py            # visar statistik
```

---

## DEL 6 — NÄR NÅGON SVARAR

1. Svara inom 2 timmar
2. Boka 15-minuterssamtal
3. Visa deras hemsida, peka på problem, presentera Bas-paketet
4. Skicka offert inom 24 timmar (50% förskott, 50% vid leverans)

### Lead Status Workflow
```
NEW → CONTACTED → FOLLOW_UP_1 → FOLLOW_UP_2 → FOLLOW_UP_3 → BREAKUP_SENT
  → REPLIED → MEETING_BOOKED → PROPOSAL_SENT → WON / LOST
  → NOT_INTERESTED → ARCHIVED
  → NO_RESPONSE (efter 21 dagar) → DEAD → RE_ENGAGE (efter 2–3 månader)
```

---

## DEL 7 — FRAMER: BYGG HEMSIDAN

### Workflow per kund
1. Samla material: logotyp, färger, foton, texter (15–45 min)
2. Generera med Framer AI + detaljerad prompt per bransch (15–30 min)
3. Polishera layout, typografi, färger (30–90 min)
4. Lägg in innehåll (30–60 min)
5. Mobilanpassa alla breakpoints — Desktop/Tablet/Mobile (20–60 min)
6. SEO-setup: meta, OG, alt-text, schema markup (10–40 min)
7. QA-checklista (15–45 min)
8. Koppla domän + SSL (10 min)
9. Kundgranskning + revisioner (30–60 min)

### Visuell skillnad mellan paket
- **Bas:** Rent men template-känsla, stockfoton, enkla sektioner, inga animationer
- **Standard:** Känns custom-designat, scroll-animationer, medveten typografi, Google Maps
- **Premium:** Ser ut som en 50 000 kr-sajt, CMS, chatbot, bokningssystem, alla detaljer finslipade

---

## DEL 8 — JURIDIK

Mejlbekräftelse = bindande avtal. Skicka alltid detta innan du börjar:

> Hej [namn], här är vad vi kommit överens om:
> ✓ [X]-sidig hemsida, mobilanpassad, kontaktformulär, max 2 revisioner
> ✗ Domän, hosting, texter = kundens ansvar
> Pris: [X] kr (50% nu, 50% vid leverans)
> Svara OK så kör vi!

Skatt: Under 20 000 kr/år = inkomst av tjänst, ingen F-skatt krävs.

---

## DEL 9 — FRAMGÅNGSMÅTT

| Vecka | Mål |
|-------|-----|
| 1 | 200 leads scrapade, 40 mejl skickade, LinkedIn live, Waalaxy igång |
| 2 | 5–10 svar, 2–3 samtal bokade |
| 3 | Första betalande kunden |
| 4 | 8 000–15 000 kr intjänat |
| Månad 2 | 15 000–25 000 kr/mån |
| Månad 3 | 20 000–35 000 kr/mån |

### Nyckeltal att övervaka

| Metric | Mål | Röd flagga |
|--------|-----|-----------|
| Öppningsfrekvens | >50% | <20% (fixa ämnesrader) |
| Svarsfrekvens | >8% | <2% (skriv om mejl) |
| LinkedIn acceptance | >35% | <25% (ändra note) |
| Bounce rate | <3% | >5% (verifiera leads) |
| Discovery calls/mån | 3–5 | 0 (omvärdera hela funneln) |

---

## DEL 10 — STARK REKOMMENDATION

**Investera 105 kr/mån i Google Workspace** så snart första betalningen kommer in:
- Skicka från `buster@brstudio.se` istället för `@gmail.com`
- ~30% bättre inbox placement
- 2 000 mejl/dag istället för 500
- Professionellt intryck (avgörande för webbdesign-tjänster)
- SPF + DKIM + DMARC-kontroll

---

*Version 3 — April 2026 — Baserad på deep research av 6 specialistagenter*
