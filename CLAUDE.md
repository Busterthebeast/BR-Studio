# BR Studio — CLAUDE.md

Komplett kontext för Claude Code. Läs detta innan du gör något i detta projekt.

---

## Vad är BR Studio?

BR Studio är en svensk webbutvecklingsbyrå driven av Buster (17 år, gymnasieelev år 2 i Stockholm). Byrån säljer professionella hemsidor till svenska småföretag — snabbt, billigt och med AI-verktyg som gör att en hemsida kan produceras på 3–5 timmar.

**Kärnlöftet till kunden:** En professionell, unik hemsida som ser ut som den kostar 50 000 kr — levererad på 5–7 dagar, till ett pris av 4 000–18 000 kr.

**Busterns roll:** Ensam founder, ensam säljare, ensam producent. Allt byggs med Framer AI + manuell polish. Inga anställda, inga partners, inga externa kostnader i fas 1.

---

## Affärsmodell

### Tjänster & Priser

| Paket | Pris | Innehåll |
|---|---|---|
| **Bas** | 4 000–6 000 kr | 1–3 sidor, mobilanpassad, grundläggande SEO, kontaktformulär |
| **Standard** | 7 000–10 000 kr | 4–6 sidor, animations, Google Analytics, anpassad design |
| **Premium** | 12 000–18 000 kr | 7+ sidor, CMS, avancerad SEO, allt i Standard + mer |
| **AI-chatbot (upsell)** | +2 000–4 000 kr | Chatbase-chatbot tränad på kundens info |
| **SEO-paket (upsell)** | +1 500–3 000 kr | Sökordsanalys, meta-tags, Google Search Console-setup |

### Intäktsmål
- Månad 1: 1 kund = 6 000 kr
- Månad 2: 2 kunder = 12 000 kr
- Månad 3+: 3–4 kunder/mån = 20 000–30 000 kr/mån

### Juridik
- Betalning via banköverföring eller Swish
- Faktura via fakturera.nu
- Mejlbekräftelse från kunden = bindande avtal
- Under ~20 000 kr/år: deklareras som inkomst av tjänst, ingen F-skatt krävs
- Kundens ansvar: GDPR, integritetspolicy, domän, Framer-hosting
- Busters ansvar: designa och leverera hemsidan

---

## Verktygsstack

### Produktion
- **Framer AI** — primärt byggverktyg. AI genererar grundlayout från prompt, Buster poliserar manuellt. Mål: 3–5h per hemsida.
- **Chatbase** — för AI-chatbot upsell. Tränas på kundens FAQ, produkter, kontaktinfo.

### Lead Generation (Fas 1 — gratis)
- **Outscraper** — scrapa leads (företagsnamn, mejl, telefon, bransch) från Google Maps och andra källor
- **Apollo.io** — komplettera leads med LinkedIn-profiler, mejladresser, befattningar
- **Waalaxy** — LinkedIn outreach, max 80 kontakter/mån på gratisplanen
- **ManyChat** — Instagram DM-automation för inkommande leads
- **Python + Gmail SMTP** — cold email-skript som skickar personaliserade mejl från Busters Gmail

### Lead Generation (Fas 2 — betald, när intäkter finns)
- **Smartlead** (~340 kr/mån) — skalbar cold email med uppvärmning och rotation
- **n8n på Hetzner** (~50 kr/mån) — ersätter Make.com, mer flexibel automation

### Automation & Workflow
- **Make.com** — kopplar ihop verktyg i fas 1 (gratis tier)
- **Google Sheets** — CRM, leadlista, pipeline-tracking
- **Carrd** — Busters egen portföljsida (gratis)
- **fakturera.nu** — fakturor och betalningshantering

---

## Försäljningsprocess

### Steg 1: Lead Scraping
Outscraper + Apollo används för att hitta svenska småföretag med:
- Dålig eller obefintlig hemsida (kontrolleras manuellt eller med verktyg)
- Aktiv verksamhet (Google Maps-recensioner, aktiv LinkedIn)
- Rätt storlek: 1–10 anställda, lokal verksamhet
- Branscher som prioriteras: restauranger, frisörer, hantverkare, butiker, konsulter

### Steg 2: Cold Email
Skript skickas via Python + Gmail. Struktur:
- Rad 1: Personaliserad observation om deras hemsida / brist på hemsida
- Rad 2–3: Kort värdeproposition (snabb, professionell, rimligt pris)
- CTA: "Kan jag visa dig ett gratis förslag på hur din hemsida skulle kunna se ut?"
- Follow-up: automatisk om inget svar inom 3 dagar

### Steg 3: LinkedIn Outreach (parallellt)
Waalaxy skickar connection requests + meddelanden till beslutsfattare (ägare, VD) på LinkedIn.

### Steg 4: Discovery Call (15 min)
Om kunden visar intresse — ett kort samtal eller mejlutbyte för att förstå:
- Vad de gör
- Vilka kunder de vill nå
- Referenssidor de gillar
- Budget och tidslinje

### Steg 5: Förslag + Offert
Skicka ett enkelt förslag (1 sida) med:
- Valt paket och pris
- Vad som ingår
- Tidsplan (leverans inom 5–7 dagar)
- Betalningsvillkor (50% förskott, 50% vid leverans)

### Steg 6: Produktion
Framer AI används för att generera grundlayout baserat på kundens info. Buster poliserar:
- Typografi och färger (matchar kundens varumärke)
- Bilder (Unsplash / kundens egna foton)
- Texter (skrivna av Buster eller AI-genererade och redigerade)
- Mobilanpassning
- SEO-grundinställningar

### Steg 7: Leverans & Betalning
- Kunden får preview-länk för feedback
- Max 2 runder av revisioner ingår
- Slutbetalning → Framer publiceras på kundens domän

---

## Busters Case Studies (används i portfolio & cold email)

### Case 1: Betalande kundhemsida
En riktig kund har redan betalat för en hemsida byggd av Buster. Används som primärt socialt bevis.

### Case 2: Henric AI Word Add-In
En komplex mjukvaruprodukt byggd av Buster: TypeScript, Office.js, Supabase backend, 40 mallar i 10 kategorier. Visar teknisk bredd och förmåga att leverera komplexa projekt.

### Case 3: n8n Lead Automation Pipeline
Buster har byggt ett automatiserat mejlkampanjsystem från en leadlista. Direkt relevant för byråns egna processer — och bevisar att han kan automation.

---

## Portföljsida (Carrd)

Busters egen portföljsida byggs på Carrd (gratis). Innehåll:
- Kort intro: vem Buster är, vad BR Studio gör
- 3 case studies med beskrivning och screenshots
- Pakettabell med priser
- Kontaktformulär / direktlänk till mejl / Calendly för bokning
- Enkelt, proffsigt, mobilanpassat

**Design-principer för portföljsidan:**
- Inte AI-generisk. Ska se ut som en riktigt byrå.
- Undvik: stock-foton av glada kontorsmänniskor, gradient-bakgrunder, generiska headlines ("We build beautiful websites")
- Använd: konkreta siffror, specifika case studies, tydliga priser, svensk text

---

## Vad detta projekt innehåller (i detta repo)

```
br-studio/
├── CLAUDE.md              ← denna fil
├── README.md
├── portfolio/             ← kod/assets för portföljsidan om den byggs i kod
├── cold-email/            ← Python-skript för cold email-automation
│   ├── scraper.py         ← lead-scraping med Outscraper API
│   ├── emailer.py         ← Gmail SMTP-skript för utskick
│   ├── leads.csv          ← leadlista (gitignored)
│   └── templates/         ← mejlmallar
├── clients/               ← en undermapp per kund
│   └── [kund-namn]/       ← Framer-export, brief, offert, kommunikation
└── docs/
    ├── sales-script.md    ← manus för discovery calls
    ├── proposal-template.md ← offertmall
    └── onboarding.md      ← vad kunden behöver skicka in
```

---

## Prioriteringar just nu (vecka 1)

1. **Portföljsida klar** — Carrd eller enkel HTML, live på en URL
2. **Cold email-skript klart** — Python + Gmail, testat och redo att skicka
3. **Leadlista: 50+ svenska småföretag** — scrapade med Outscraper
4. **Första utskick skickat** — minst 20 mejl dag 1 (onsdag 8 april 2026)
5. **LinkedIn Waalaxy uppe** — 10+ connection requests skickade

---

## Constraints för all kod i detta projekt

- All kundkommunikation och texter är på **svenska**
- Inga tunga frameworks för enkla saker — använd Python stdlib där det räcker
- API-nycklar och mejladresser läggs alltid i `.env`, aldrig i koden
- `leads.csv` och `.env` är alltid gitignored (innehåller personuppgifter)
- Håll skripten enkla och läsbara — Buster ska kunna köra och felsöka dem själv
