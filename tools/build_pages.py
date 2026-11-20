#!/usr/bin/env python3
"""Authoring tool: generates the static localized HTML pages (index/trip/privacy
per locale) + sitemap.xml. NOT a runtime build step — the generated files are
committed and GitHub Pages serves them as-is. Re-run after editing copy here.
"""
import json
import os
from string import Template

SITE = "https://scoperta.app"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOCALES = {
    "cs": {
        "lang": "cs", "dir": "", "og_locale": "cs_CZ",
        "title": "Scoperta — AI plánovač výletů | Kam na výlet s dětmi i se psem",
        "desc": "Napiš, odkud vyrážíš a s kým — Scoperta ti naplánuje celý den: zastávky, oběd, vyhlídku i mapu. AI plánovač výletů pro rodiny s dětmi, se psem i ve dvou.",
        "h1": "Napiš, odkud vyrážíš a s kým. <em>AI naplánuje celý den.</em>",
        "sub": "Zastávky, oběd i vyhlídka po cestě — hotový plán jednodenního výletu s mapou. Zvládne děti, psa i „překvap mě“.",
        "origin_label": "Odkud vyrážíš", "origin_ph": "např. Brno",
        "area_label": "Kam / oblast", "area_hint": "(nepovinné)", "area_ph": "nech prázdné a překvapíme tě",
        "radius_label": "Jak daleko max?", "radius_unit": "km",
        "companions_label": "S kým jedeš",
        "chips": {"kids": "👨‍👩‍👧 s dětmi", "dog": "🐕 se psem", "couple": "💑 ve dvou", "friends": "🧑‍🤝‍🧑 s partou", "solo": "🚶 sólo"},
        "date_label": "Kdy", "pace_label": "Tempo",
        "pace_relaxed": "Pohodové", "pace_active": "Aktivní",
        "cta": "Naplánovat výlet",
        "loading_note": "Obvykle to trvá 15–40 vteřin — AI mezitím vybírá zastávky a skládá trasu.",
        "share": "📤 Sdílet", "print": "🖨️ Tisk", "variant": "✨ Jiná varianta",
        "how_title": "Jak to funguje",
        "steps": [
            ("Napiš, odkud a s kým", "Stačí město, odkud vyrážíš. Cíl můžeš nechat na nás — jen řekni, jak daleko se ti chce jet."),
            ("AI poskládá den", "Vybere zastávky, naplánuje kde se najíst a spočítá časy tak, aby den dával smysl."),
            ("Vyraz podle mapy", "Hotový itinerář máš na mapě i v přehledné časové ose. Pošli ho ostatním nebo si ho vytiskni."),
        ],
        "faq_title": "Časté otázky",
        "faq": [
            ("Co Scoperta umí?", "Naplánuje ti jednodenní výlet autem: kam jet, kde zastavit, kde se naobědvat a kdy vyrazit zpátky. Výsledek dostaneš jako časovou osu se zastávkami a mapou."),
            ("Je to zdarma?", "Naplánování výletu je zdarma, bez registrace. Kdo chce plánovat víc výletů denně a ukládat si je, tomu je určena připravovaná Scoperta Plus."),
            ("Jak funguje „překvap mě“?", "Když necháš cíl prázdný, nastavíš jen okruh v kilometrech a Scoperta sama vybere hezké místo, které to od tebe nemá daleko."),
            ("Počítá plán s dětmi a se psem?", "Ano. Když zaškrtneš, že jedou děti nebo pes, vybíráme místa, kde jsou vítaní, a u zastávek uvidíš poznámky přímo pro ně."),
            ("Musím se registrovat?", "Ne. Zadáš odkud a s kým, a za chvíli máš plán. Žádný účet, žádný e-mail."),
        ],
        "footer_contact": "Napiš nám", "footer_privacy": "Ochrana soukromí",
        "footer_tag": "Scoperta — jednodenní výlety plánované AI.",
        "pw_title": "Scoperta Plus", "pw_sub": "Víc výletů, víc objevování.",
        "pw_features": ["Neomezené výlety každý den", "Uložené výlety na jednom místě", "Brzy: mobilní aplikace"],
        "pw_monthly": "Měsíčně", "pw_monthly_price": "99 Kč/měs",
        "pw_yearly": "Ročně", "pw_yearly_price": "599 Kč/rok",
        "pw_founder": "Zakládající členství: první měsíc neúčtujeme, kdykoli zrušíš.",
        "pw_fb_title": "Už brzy!",
        "pw_fb_text": "Scoperta Plus právě dokončujeme. Napiš nám a dáme ti vědět mezi prvními — jako zakládající člen budeš mít první měsíc zdarma.",
        "pw_fb_cta": "Chci vědět první",
        "cookie_text": "Souhlasíš s měřením používání Scoperty pomocí našeho Tassella?",
        "analytics_settings": "Nastavení analytiky",
        "cookie_yes": "Povolit", "cookie_no": "Ne, díky",
        "trip_title": "Sdílený výlet | Scoperta",
        "trip_desc": "Podívej se na jednodenní výlet naplánovaný AI plánovačem Scoperta — zastávky, oběd i mapa.",
        "trip_intro_h": "Sdílený výlet",
        "trip_intro_p": "Tady se zobrazí výlet, který ti někdo poslal. Odkaz musí obsahovat kód výletu — pokud vidíš tuhle zprávu, otevři odkaz přesně tak, jak ti přišel.",
        "trip_cta": "Naplánovat vlastní výlet",
        "privacy_title": "Ochrana soukromí | Scoperta",
        "privacy_h1": "Ochrana soukromí",
        "privacy_body": """
<p>Scoperta je jednoduchá webová služba pro plánování výletů. K soukromí přistupujeme stejně jednoduše:</p>
<h2>Co zpracováváme</h2>
<ul>
<li><strong>Zadání formuláře</strong> (odkud, kam, s kým, datum, tempo) posíláme na náš server jen proto, abychom vygenerovali itinerář. Neukládáme ho k žádnému účtu — žádné účty nemáme.</li>
<li><strong>Denní limit</strong> výletů zdarma hlídáme podle IP adresy a v prohlížeči (localStorage). Nic z toho nespojujeme s tvojí identitou.</li>
<li><strong>Sdílené výlety</strong> dostanou anonymní odkaz. Kdo má odkaz, výlet uvidí.</li>
</ul>
<h2>Analytika</h2>
<p>Po povolení analytiky Tassello přiřadí prohlížeči náhodné ID. Měří zobrazené stránky, kroky plánování, typ zařízení, jazyk stránky a stav a dobu odezvy dvou typů požadavků na náš server. Obsah formulářů, místa, sdílecí odkazy ani těla požadavků nesbíráme. Při výpadku čekají události v prohlížeči. Při dalším pokusu se události starší sedmi dnů zahodí. Volbu můžeš změnit v nastavení analytiky v patičce. Odmítnutí odstraní místní ID a neodeslané události.</p>
<h2>Kontakt</h2>
<p>Cokoli k soukromí: <a href="mailto:hello@scoperta.app">hello@scoperta.app</a>.</p>
""",
        "back_home": "← Zpět na Scopertu",
        "price_m": "99", "price_y": "599", "currency": "CZK",
    },
    "en": {
        "lang": "en", "dir": "en/", "og_locale": "en_US",
        "title": "Scoperta — AI Day Trip Planner | Trips with Kids & Dogs",
        "desc": "Tell Scoperta where you're starting from and who's coming along — it plans your whole day out: stops, lunch, a viewpoint and a map. AI day trip planner for families, dog owners and couples.",
        "h1": "Tell us where you start and who's coming. <em>AI plans your whole day.</em>",
        "sub": "Stops, lunch and a viewpoint along the way — a ready-made day trip plan with a map. Works with kids, dogs, or “surprise me”.",
        "origin_label": "Starting from", "origin_ph": "e.g. Munich",
        "area_label": "Where to / area", "area_hint": "(optional)", "area_ph": "leave empty and we'll surprise you",
        "radius_label": "How far at most?", "radius_unit": "km",
        "companions_label": "Who's coming",
        "chips": {"kids": "👨‍👩‍👧 kids", "dog": "🐕 dog", "couple": "💑 just us two", "friends": "🧑‍🤝‍🧑 friends", "solo": "🚶 solo"},
        "date_label": "When", "pace_label": "Pace",
        "pace_relaxed": "Relaxed", "pace_active": "Active",
        "cta": "Plan my day",
        "loading_note": "This usually takes 15–40 seconds — the AI is picking stops and building your route.",
        "share": "📤 Share", "print": "🖨️ Print", "variant": "✨ Another idea",
        "how_title": "How it works",
        "steps": [
            ("Say where & who", "Just the town you're starting from. You can leave the destination to us — only say how far you're willing to drive."),
            ("AI builds your day", "It picks the stops, plans where to eat and works out the timing so the day actually flows."),
            ("Follow the map", "You get the itinerary as a timeline and a map. Share it with the others or print it out."),
        ],
        "faq_title": "Frequently asked questions",
        "faq": [
            ("What does Scoperta do?", "It plans a one-day trip by car: where to go, where to stop, where to have lunch and when to head back. You get a timeline of stops plus a map."),
            ("Is it free?", "Planning a trip is free, no sign-up needed. If you want to plan more trips per day and save them, that's what the upcoming Scoperta Plus is for."),
            ("How does “surprise me” work?", "Leave the destination empty, set a radius in kilometres, and Scoperta picks a lovely place within reach on its own."),
            ("Does it account for kids and dogs?", "Yes. Tick that kids or a dog are coming and we favour places where they're welcome — stops get notes written just for them."),
            ("Do I need an account?", "No. Type where you start and who's coming, and you'll have a plan in under a minute. No account, no email."),
        ],
        "footer_contact": "Contact us", "footer_privacy": "Privacy",
        "footer_tag": "Scoperta — day trips planned by AI.",
        "pw_title": "Scoperta Plus", "pw_sub": "More trips, more discovering.",
        "pw_features": ["Unlimited trips every day", "Saved trips in one place", "Coming soon: mobile app"],
        "pw_monthly": "Monthly", "pw_monthly_price": "€3.99/mo",
        "pw_yearly": "Yearly", "pw_yearly_price": "€23.99/yr",
        "pw_founder": "Founding membership: first month on us, cancel anytime.",
        "pw_fb_title": "Coming soon!",
        "pw_fb_text": "We're just finishing Scoperta Plus. Drop us a line and you'll be among the first to know — founding members get the first month free.",
        "pw_fb_cta": "Keep me posted",
        "cookie_text": "Allow Scoperta to measure usage with our own Tassello analytics?",
        "analytics_settings": "Analytics settings",
        "cookie_yes": "Allow", "cookie_no": "No thanks",
        "trip_title": "Shared Trip | Scoperta",
        "trip_desc": "Take a look at a day trip planned by Scoperta, the AI day trip planner — stops, lunch and a map.",
        "trip_intro_h": "Shared trip",
        "trip_intro_p": "This page shows a trip someone shared with you. The link must contain a trip code — if you're seeing this message, open the link exactly as you received it.",
        "trip_cta": "Plan my own trip",
        "privacy_title": "Privacy | Scoperta",
        "privacy_h1": "Privacy",
        "privacy_body": """
<p>Scoperta is a simple web service for planning day trips. We keep privacy just as simple:</p>
<h2>What we process</h2>
<ul>
<li><strong>Your form input</strong> (start, destination, companions, date, pace) is sent to our server only to generate the itinerary. It isn't stored under any account — we don't have accounts.</li>
<li><strong>The daily free limit</strong> is enforced by IP address and in your browser (localStorage). None of it is linked to your identity.</li>
<li><strong>Shared trips</strong> get an anonymous link. Anyone with the link can view the trip.</li>
</ul>
<h2>Analytics</h2>
<p>If you allow analytics, Tassello assigns your browser a random ID. It records page views, planning steps, device class, page language, and the status and duration of two types of request to our server. We exclude form contents, locations, share links and request bodies. Pending events are stored in your browser. On the next attempt we discard events older than seven days. Use Analytics settings in the footer to change your choice. Declining removes the local ID and pending events.</p>
<h2>Contact</h2>
<p>Anything privacy-related: <a href="mailto:hello@scoperta.app">hello@scoperta.app</a>.</p>
""",
        "back_home": "← Back to Scoperta",
        "price_m": "3.99", "price_y": "23.99", "currency": "EUR",
    },
    "de": {
        "lang": "de", "dir": "de/", "og_locale": "de_DE",
        "title": "Scoperta — Ausflugsplaner mit KI | Tagesausflug mit Kindern & Hund",
        "desc": "Sag Scoperta, wo du startest und wer mitkommt — und die KI plant deinen ganzen Tagesausflug: Stopps, Mittagessen, Aussichtspunkt und Karte. Ideal für Familien, Hundebesitzer und Paare.",
        "h1": "Sag, wo du startest und wer mitkommt. <em>Die KI plant deinen ganzen Tag.</em>",
        "sub": "Stopps, Mittagessen und ein Aussichtspunkt unterwegs — ein fertiger Tagesplan mit Karte. Klappt mit Kindern, Hund oder „überrasch mich“.",
        "origin_label": "Startort", "origin_ph": "z. B. München",
        "area_label": "Wohin / Region", "area_hint": "(optional)", "area_ph": "leer lassen und wir überraschen dich",
        "radius_label": "Wie weit höchstens?", "radius_unit": "km",
        "companions_label": "Wer kommt mit",
        "chips": {"kids": "👨‍👩‍👧 Kinder", "dog": "🐕 Hund", "couple": "💑 zu zweit", "friends": "🧑‍🤝‍🧑 Freunde", "solo": "🚶 solo"},
        "date_label": "Wann", "pace_label": "Tempo",
        "pace_relaxed": "Gemütlich", "pace_active": "Aktiv",
        "cta": "Ausflug planen",
        "loading_note": "Das dauert meist 15–40 Sekunden — die KI wählt gerade Stopps aus und baut deine Route.",
        "share": "📤 Teilen", "print": "🖨️ Drucken", "variant": "✨ Andere Idee",
        "how_title": "So funktioniert's",
        "steps": [
            ("Sag, wo und mit wem", "Es reicht der Ort, an dem du startest. Das Ziel kannst du uns überlassen — sag nur, wie weit du fahren magst."),
            ("Die KI baut deinen Tag", "Sie wählt die Stopps, plant, wo ihr esst, und rechnet die Zeiten so, dass der Tag rund läuft."),
            ("Fahr nach Karte", "Den fertigen Plan bekommst du als Zeitleiste und Karte. Teil ihn mit den anderen oder druck ihn aus."),
        ],
        "faq_title": "Häufige Fragen",
        "faq": [
            ("Was kann Scoperta?", "Sie plant einen Tagesausflug mit dem Auto: wohin, wo anhalten, wo zu Mittag essen und wann zurückfahren. Du bekommst eine Zeitleiste mit Stopps und eine Karte."),
            ("Ist das kostenlos?", "Einen Ausflug zu planen ist kostenlos, ohne Registrierung. Wer täglich mehr Ausflüge planen und speichern will, für den ist das kommende Scoperta Plus gedacht."),
            ("Wie funktioniert „überrasch mich“?", "Lass das Ziel leer und stell nur den Umkreis in Kilometern ein — Scoperta sucht dann selbst ein schönes Ziel in deiner Reichweite aus."),
            ("Werden Kinder und Hunde berücksichtigt?", "Ja. Wenn du angibst, dass Kinder oder ein Hund mitkommen, bevorzugen wir Orte, an denen sie willkommen sind — mit eigenen Hinweisen bei den Stopps."),
            ("Muss ich mich registrieren?", "Nein. Du tippst ein, wo du startest und wer mitkommt — kurz darauf steht dein Plan. Kein Konto, keine E-Mail."),
        ],
        "footer_contact": "Schreib uns", "footer_privacy": "Datenschutz",
        "footer_tag": "Scoperta — Tagesausflüge, geplant von KI.",
        "pw_title": "Scoperta Plus", "pw_sub": "Mehr Ausflüge, mehr entdecken.",
        "pw_features": ["Unbegrenzte Ausflüge jeden Tag", "Gespeicherte Ausflüge an einem Ort", "Bald: mobile App"],
        "pw_monthly": "Monatlich", "pw_monthly_price": "3,99 €/Monat",
        "pw_yearly": "Jährlich", "pw_yearly_price": "23,99 €/Jahr",
        "pw_founder": "Gründungsmitgliedschaft: den ersten Monat berechnen wir nicht, jederzeit kündbar.",
        "pw_fb_title": "Bald verfügbar!",
        "pw_fb_text": "Scoperta Plus ist fast fertig. Schreib uns und du erfährst es als eine/r der Ersten — Gründungsmitglieder bekommen den ersten Monat gratis.",
        "pw_fb_cta": "Haltet mich auf dem Laufenden",
        "cookie_text": "Darf Scoperta die Nutzung mit unserer eigenen Statistik Tassello messen?",
        "analytics_settings": "Statistik-Einstellungen",
        "cookie_yes": "Erlauben", "cookie_no": "Nein, danke",
        "trip_title": "Geteilter Ausflug | Scoperta",
        "trip_desc": "Schau dir einen Tagesausflug an, geplant mit Scoperta, dem KI-Ausflugsplaner — Stopps, Mittagessen und Karte.",
        "trip_intro_h": "Geteilter Ausflug",
        "trip_intro_p": "Hier erscheint ein Ausflug, den dir jemand geschickt hat. Der Link muss einen Ausflugscode enthalten — wenn du diese Meldung siehst, öffne den Link genau so, wie du ihn bekommen hast.",
        "trip_cta": "Eigenen Ausflug planen",
        "privacy_title": "Datenschutz | Scoperta",
        "privacy_h1": "Datenschutz",
        "privacy_body": """
<p>Scoperta ist ein einfacher Web-Dienst zum Planen von Tagesausflügen. Beim Datenschutz bleiben wir genauso einfach:</p>
<h2>Was wir verarbeiten</h2>
<ul>
<li><strong>Deine Formulareingaben</strong> (Start, Ziel, Begleitung, Datum, Tempo) schicken wir nur an unseren Server, um den Reiseplan zu erstellen. Sie werden keinem Konto zugeordnet — es gibt keine Konten.</li>
<li><strong>Das tägliche Gratis-Limit</strong> prüfen wir über die IP-Adresse und im Browser (localStorage). Nichts davon wird mit deiner Identität verknüpft.</li>
<li><strong>Geteilte Ausflüge</strong> bekommen einen anonymen Link. Wer den Link hat, sieht den Ausflug.</li>
</ul>
<h2>Statistik</h2>
<p>Nach deiner Zustimmung vergibt Tassello eine zufällige Browser-ID. Erfasst werden Seitenaufrufe, Planungsschritte, Gerätetyp, Seitensprache sowie Status und Dauer von zwei Arten von Serveranfragen. Formularinhalte, Orte, Freigabelinks und Anfrageinhalte werden ausgeschlossen. Ausstehende Ereignisse bleiben im Browser. Beim nächsten Versuch verwerfen wir Ereignisse, die älter als sieben Tage sind. In den Statistik-Einstellungen am Seitenende kannst du deine Wahl ändern. Ablehnen entfernt die lokale ID und ausstehende Ereignisse.</p>
<h2>Kontakt</h2>
<p>Alles rund um Datenschutz: <a href="mailto:hello@scoperta.app">hello@scoperta.app</a>.</p>
""",
        "back_home": "← Zurück zu Scoperta",
        "price_m": "3.99", "price_y": "23.99", "currency": "EUR",
    },
    "it": {
        "lang": "it", "dir": "it/", "og_locale": "it_IT",
        "title": "Scoperta — Gite fuori porta con l'AI | Itinerari con bambini e cane",
        "desc": "Di' a Scoperta da dove parti e con chi — e l'AI organizza la tua gita di un giorno: tappe, pranzo, punto panoramico e mappa. Perfetta per famiglie, cani e coppie.",
        "h1": "Dicci da dove parti e con chi. <em>L'AI organizza tutta la giornata.</em>",
        "sub": "Tappe, pranzo e un punto panoramico lungo la strada — un piano pronto per la gita, con la mappa. Funziona con bambini, cane o «sorprendimi».",
        "origin_label": "Da dove parti", "origin_ph": "es. Verona",
        "area_label": "Dove / zona", "area_hint": "(facoltativo)", "area_ph": "lascia vuoto e ti sorprendiamo",
        "radius_label": "Quanto lontano al massimo?", "radius_unit": "km",
        "companions_label": "Con chi vai",
        "chips": {"kids": "👨‍👩‍👧 bambini", "dog": "🐕 cane", "couple": "💑 in coppia", "friends": "🧑‍🤝‍🧑 amici", "solo": "🚶 da solo/a"},
        "date_label": "Quando", "pace_label": "Ritmo",
        "pace_relaxed": "Rilassato", "pace_active": "Attivo",
        "cta": "Organizza la gita",
        "loading_note": "Di solito ci vogliono 15–40 secondi — l'AI sta scegliendo le tappe e componendo il percorso.",
        "share": "📤 Condividi", "print": "🖨️ Stampa", "variant": "✨ Un'altra idea",
        "how_title": "Come funziona",
        "steps": [
            ("Dicci da dove e con chi", "Basta la città da cui parti. La meta puoi lasciarla a noi — dicci solo quanti chilometri sei disposto a fare."),
            ("L'AI compone la giornata", "Sceglie le tappe, decide dove si mangia bene e calcola i tempi perché la giornata fili liscia."),
            ("Parti con la mappa", "L'itinerario pronto lo trovi sulla mappa e in una comoda linea del tempo. Condividilo o stampalo."),
        ],
        "faq_title": "Domande frequenti",
        "faq": [
            ("Cosa fa Scoperta?", "Organizza una gita di un giorno in auto: dove andare, dove fermarsi, dove pranzare e quando rientrare. Il risultato è una linea del tempo con le tappe e una mappa."),
            ("È gratis?", "Organizzare una gita è gratuito, senza registrazione. Per chi vuole pianificare più gite al giorno e salvarle arriverà Scoperta Plus."),
            ("Come funziona «sorprendimi»?", "Lascia vuota la meta e imposta solo il raggio in chilometri: Scoperta sceglierà da sola un bel posto a portata di mano."),
            ("Tiene conto di bambini e cani?", "Sì. Se indichi che vengono bambini o il cane, preferiamo posti dove sono benvenuti — e alle tappe trovi note pensate per loro."),
            ("Devo registrarmi?", "No. Scrivi da dove parti e con chi, e in meno di un minuto hai il piano. Niente account, niente email."),
        ],
        "footer_contact": "Scrivici", "footer_privacy": "Privacy",
        "footer_tag": "Scoperta — gite di un giorno organizzate dall'AI.",
        "pw_title": "Scoperta Plus", "pw_sub": "Più gite, più scoperte.",
        "pw_features": ["Gite illimitate ogni giorno", "Gite salvate in un unico posto", "In arrivo: app mobile"],
        "pw_monthly": "Mensile", "pw_monthly_price": "3,99 €/mese",
        "pw_yearly": "Annuale", "pw_yearly_price": "23,99 €/anno",
        "pw_founder": "Iscrizione da fondatore: il primo mese non lo addebitiamo, disdici quando vuoi.",
        "pw_fb_title": "In arrivo!",
        "pw_fb_text": "Stiamo ultimando Scoperta Plus. Scrivici e sarai tra i primi a saperlo — i membri fondatori hanno il primo mese gratis.",
        "pw_fb_cta": "Tenetemi aggiornato",
        "cookie_text": "Consenti a Scoperta di misurare l’utilizzo con il nostro servizio Tassello?",
        "analytics_settings": "Impostazioni statistiche",
        "cookie_yes": "Consenti", "cookie_no": "No, grazie",
        "trip_title": "Gita condivisa | Scoperta",
        "trip_desc": "Guarda una gita di un giorno organizzata da Scoperta, il pianificatore di gite con AI — tappe, pranzo e mappa.",
        "trip_intro_h": "Gita condivisa",
        "trip_intro_p": "Qui compare una gita che qualcuno ti ha inviato. Il link deve contenere il codice della gita — se vedi questo messaggio, apri il link esattamente come ti è arrivato.",
        "trip_cta": "Organizza la tua gita",
        "privacy_title": "Privacy | Scoperta",
        "privacy_h1": "Privacy",
        "privacy_body": """
<p>Scoperta è un semplice servizio web per organizzare gite di un giorno. Anche con la privacy restiamo semplici:</p>
<h2>Cosa trattiamo</h2>
<ul>
<li><strong>I dati del modulo</strong> (partenza, meta, compagni, data, ritmo) vengono inviati al nostro server solo per generare l'itinerario. Non vengono associati ad alcun account — non esistono account.</li>
<li><strong>Il limite giornaliero gratuito</strong> viene controllato tramite indirizzo IP e nel browser (localStorage). Nulla di tutto ciò è collegato alla tua identità.</li>
<li><strong>Le gite condivise</strong> ricevono un link anonimo. Chi ha il link può vedere la gita.</li>
</ul>
<h2>Statistiche</h2>
<p>Con il tuo consenso Tassello assegna al browser un ID casuale. Registra le pagine viste, i passaggi di pianificazione, il tipo di dispositivo, la lingua e lo stato e la durata di due tipi di richieste al nostro server. Escludiamo contenuti dei moduli, luoghi, link di condivisione e corpi delle richieste. Gli eventi in attesa restano nel browser. Al tentativo successivo scartiamo quelli più vecchi di sette giorni. Puoi cambiare scelta nelle impostazioni statistiche a piè di pagina. Il rifiuto elimina l’ID locale e gli eventi in attesa.</p>
<h2>Contatti</h2>
<p>Per qualsiasi domanda sulla privacy: <a href="mailto:hello@scoperta.app">hello@scoperta.app</a>.</p>
""",
        "back_home": "← Torna a Scoperta",
        "price_m": "3.99", "price_y": "23.99", "currency": "EUR",
    },
}

ORDER = ["cs", "en", "de", "it"]


def hreflang_links(page):
    """page: '' (home), 'trip.html', 'privacy.html'"""
    lines = []
    for lc in ORDER:
        d = LOCALES[lc]["dir"]
        lines.append('<link rel="alternate" hreflang="%s" href="%s/%s%s">' % (lc, SITE, d, page))
    lines.append('<link rel="alternate" hreflang="x-default" href="%s/en/%s">' % (SITE, page))
    return "\n".join(lines)


def lang_nav(locale, page):
    """Relative language switcher links."""
    rel_root = "../" if LOCALES[locale]["dir"] else ""
    items = []
    for lc in ORDER:
        target = rel_root + LOCALES[lc]["dir"] + page
        if not target:
            target = "./"
        cur = ' aria-current="true"' if lc == locale else ""
        items.append('<a href="%s" data-lang="%s" hreflang="%s"%s>%s</a>' % (target, lc, lc, cur, lc.upper()))
    return '<nav class="lang-switch" aria-label="Language">%s</nav>' % "".join(items)


def head(L, page, page_title, page_desc):
    d = L["dir"]
    canonical = "%s/%s%s" % (SITE, d, page)
    a = ("../" if d else "") + "assets/"
    og_img = "%s/assets/og/%s.png" % (SITE, L["lang"])
    return Template("""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title>
<meta name="description" content="${desc}">
<meta name="theme-color" content="#1E5A3C" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1A14" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="${canonical}">
${hreflang}
<link rel="icon" href="${a}favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="${a}favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="${a}apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Scoperta">
<meta property="og:locale" content="${og_locale}">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${title}">
<meta name="twitter:description" content="${desc}">
<meta name="twitter:image" content="${og_img}">
<link rel="stylesheet" href="${a}app.css">
<link rel="preconnect" href="https://unpkg.com" crossorigin>
<link rel="dns-prefetch" href="https://tile.openstreetmap.org">
<script defer src="${a}config.js"></script>
<script defer src="${a}i18n/${lang}.js"></script>
<script defer src="${a}analytics.js"></script>
<script defer src="${a}app.js"></script>""").substitute(
        title=page_title, desc=page_desc, canonical=canonical,
        hreflang=hreflang_links(page), a=a, og_locale=L["og_locale"],
        og_img=og_img, lang=L["lang"])


def jsonld_webapp(L):
    data = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Scoperta",
        "url": "%s/%s" % (SITE, L["dir"]),
        "description": L["desc"],
        "applicationCategory": "TravelApplication",
        "operatingSystem": "Web",
        "inLanguage": L["lang"],
        "offers": [
            {"@type": "Offer", "name": "Scoperta Plus (monthly)", "price": L["price_m"], "priceCurrency": L["currency"]},
            {"@type": "Offer", "name": "Scoperta Plus (yearly)", "price": L["price_y"], "priceCurrency": L["currency"]},
        ],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False)


def jsonld_faq(L):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in L["faq"]
        ],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False)


def header_html(L, page):
    rel_root = "../" if L["dir"] else ""
    home = rel_root + L["dir"] if False else (rel_root if L["dir"] else "./")
    a = rel_root + "assets/"
    return ('<header class="site-header">\n'
            '<a class="brand" href="%s"><img src="%sfavicon.svg" alt="" width="30" height="30">Scoperta</a>\n'
            '%s\n</header>' % (home if home else "./", a, lang_nav(L["lang"], page)))


def footer_html(L, extra_langs_page):
    rel_root = "../" if L["dir"] else ""
    privacy = rel_root + L["dir"] + "privacy.html"
    return Template("""<footer class="site-footer">
<div class="wrap">
<div class="foot-links">
<a href="mailto:hello@scoperta.app">${contact}</a>
<a href="${privacy}">${privacy_label}</a>
<button id="analytics-choice" class="analytics-choice" type="button" hidden>${analytics_settings}</button>
</div>
<p>${tag}</p>
</div>
</footer>""").substitute(contact=L["footer_contact"], privacy=privacy,
                         privacy_label=L["footer_privacy"], analytics_settings=L["analytics_settings"], tag=L["footer_tag"])


def paywall_html(L):
    feats = "\n".join("<li>%s</li>" % f for f in L["pw_features"])
    return Template("""<div id="paywall" class="modal-backdrop" hidden>
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="pw-title">
<button class="close" type="button" aria-label="Close">✕</button>
<div id="paywall-main">
<span class="plus-badge">Scoperta Plus</span>
<h2 id="pw-title">${sub}</h2>
<ul>
${feats}
</ul>
<div class="plans">
<button class="plan-btn" type="button" data-plan="monthly"><span>${m}</span><span class="price">${mp}</span></button>
<button class="plan-btn secondary" type="button" data-plan="yearly"><span>${y}</span><span class="price">${yp}</span></button>
</div>
<p class="founder-note">${founder}</p>
</div>
<div id="paywall-fallback" class="member-fallback" hidden>
<span class="plus-badge">Scoperta Plus</span>
<h2>${fb_title}</h2>
<p>${fb_text}</p>
<p style="margin-top:14px"><a class="btn btn-accent" href="mailto:hello@scoperta.app?subject=Scoperta%20Plus">${fb_cta}</a></p>
</div>
</div>
</div>""").substitute(sub=L["pw_sub"], feats=feats, m=L["pw_monthly"], mp=L["pw_monthly_price"],
                      y=L["pw_yearly"], yp=L["pw_yearly_price"], founder=L["pw_founder"],
                      fb_title=L["pw_fb_title"], fb_text=L["pw_fb_text"], fb_cta=L["pw_fb_cta"])


def cookie_html(L):
    return Template("""<div id="cookie-bar" class="cookie-bar" hidden>
<p>${text}</p>
<button id="cookie-accept" class="btn btn-accent" type="button">${yes}</button>
<button id="cookie-decline" class="btn" type="button">${no}</button>
</div>""").substitute(text=L["cookie_text"], yes=L["cookie_yes"], no=L["cookie_no"])


def result_section(L, with_variant=True):
    variant = ('<button id="variant-btn" class="btn" type="button">%s</button>' % L["variant"]) if with_variant else ""
    return Template("""<section id="result" class="result wrap" hidden aria-live="polite">
<h2 id="result-title"></h2>
<p id="result-summary" class="summary"></p>
<div id="result-meta" class="meta"></div>
<div id="packing" class="packing" hidden></div>
<ol id="timeline" class="timeline"></ol>
<div id="map" role="img" aria-label="Map"></div>
<div class="result-actions">
<button id="share-btn" class="btn btn-accent" type="button">${share}</button>
<button id="print-btn" class="btn" type="button">${print}</button>
${variant}
</div>
<div id="tips" class="tips" hidden>
<h3>${tips_title}</h3>
<p id="tips-text"></p>
</div>
</section>""").substitute(share=L["share"], print=L["print"], variant=variant,
                          tips_title="💡 " + {"cs": "Tipy na cestu", "en": "Tips for the road",
                                              "de": "Tipps für unterwegs", "it": "Consigli per il viaggio"}[L["lang"]])


def index_page(L):
    chips = "\n".join(
        '<button type="button" class="chip" data-value="%s" aria-pressed="false">%s</button>' % (k, v)
        for k, v in L["chips"].items())
    steps = "\n".join("<li><h3>%s</h3><p>%s</p></li>" % (h, p) for h, p in L["steps"])
    faq = "\n".join("<details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in L["faq"])
    body = Template("""<a class="skip-link" href="#main">&#8595;</a>
${header}
<main id="main">
<section class="hero wrap">
<h1>${h1}</h1>
<p class="sub">${sub}</p>
<form id="trip-form" class="trip-form" novalidate="">
<div class="row-2">
<div class="field">
<label for="origin">${origin_label}</label>
<input type="text" id="origin" name="origin" required autocomplete="off" placeholder="${origin_ph}">
</div>
<div class="field">
<label for="area">${area_label} <span class="hint">${area_hint}</span></label>
<input type="text" id="area" name="area" autocomplete="off" placeholder="${area_ph}">
</div>
</div>
<div class="field radius-field" id="radius-field">
<label for="radius">${radius_label} <output id="radius-out" for="radius">50</output>&nbsp;${radius_unit}</label>
<input type="range" id="radius" name="radius" min="20" max="120" step="5" value="50">
</div>
<div class="field">
<span class="chips-label" id="companions-label"><label>${companions_label}</label></span>
<div class="chips" role="group" aria-labelledby="companions-label">
${chips}
</div>
</div>
<div class="row-2">
<div class="field">
<label for="date">${date_label}</label>
<input type="date" id="date" name="date">
</div>
<div class="field">
<span class="chips-label" id="pace-label"><label>${pace_label}</label></span>
<div class="segmented" role="group" aria-labelledby="pace-label">
<button type="button" data-pace="relaxed" aria-pressed="true">${pace_relaxed}</button>
<button type="button" data-pace="active" aria-pressed="false">${pace_active}</button>
</div>
</div>
</div>
<p id="form-error" class="form-error" hidden></p>
<button type="submit" id="submit-btn" class="cta">${cta}</button>
</form>
</section>
<section id="loading" class="loading wrap" hidden aria-live="polite">
<div class="spinner" aria-hidden="true"></div>
<p class="msg" id="loading-msg"></p>
<p class="note">${loading_note}</p>
<div class="skeleton" aria-hidden="true"><div></div><div></div><div></div></div>
</section>
${result}
<section class="how wrap">
<h2>${how_title}</h2>
<ol class="steps">
${steps}
</ol>
</section>
<section class="faq wrap">
<h2>${faq_title}</h2>
${faq}
</section>
</main>
${footer}
${paywall}
${cookie}""").substitute(
        header=header_html(L, ""), h1=L["h1"], sub=L["sub"],
        origin_label=L["origin_label"], origin_ph=L["origin_ph"],
        area_label=L["area_label"], area_hint=L["area_hint"], area_ph=L["area_ph"],
        radius_label=L["radius_label"], radius_unit=L["radius_unit"],
        companions_label=L["companions_label"], chips=chips,
        date_label=L["date_label"], pace_label=L["pace_label"],
        pace_relaxed=L["pace_relaxed"], pace_active=L["pace_active"],
        cta=L["cta"], loading_note=L["loading_note"],
        result=result_section(L, with_variant=True),
        how_title=L["how_title"], steps=steps,
        faq_title=L["faq_title"], faq=faq,
        footer=footer_html(L, ""), paywall=paywall_html(L), cookie=cookie_html(L))
    return page_shell(L, "", L["title"], L["desc"], body,
                      jsonld_webapp(L) + "\n" + jsonld_faq(L))


def trip_page(L):
    rel_root = "../" if L["dir"] else ""
    home = rel_root if L["dir"] else "./"
    body = Template("""${header}
<main id="trip-page">
<section class="hero wrap">
<div id="trip-intro" class="trip-hint">
<h1>${intro_h}</h1>
<p>${intro_p}</p>
<p style="margin-top:14px"><a class="btn btn-accent" href="${home}">${cta}</a></p>
</div>
<p id="trip-status" class="form-error" hidden aria-live="polite"></p>
</section>
${result}
<section class="wrap tips-cta" style="padding:18px 0 30px">
<a class="btn" href="${home}">${cta}</a>
</section>
</main>
${footer}
${cookie}""").substitute(
        header=header_html(L, "trip.html"),
        intro_h=L["trip_intro_h"], intro_p=L["trip_intro_p"],
        home=home, cta=L["trip_cta"],
        result=result_section(L, with_variant=False),
        footer=footer_html(L, "trip.html"), cookie=cookie_html(L))
    return page_shell(L, "trip.html", L["trip_title"], L["trip_desc"], body, "")


def privacy_page(L):
    rel_root = "../" if L["dir"] else ""
    home = rel_root if L["dir"] else "./"
    body = Template("""${header}
<main>
<article class="prose wrap">
<h1>${h1}</h1>
${content}
<p style="margin-top:24px"><a href="${home}">${back}</a></p>
</article>
</main>
${footer}
${cookie}""").substitute(
        cookie=cookie_html(L), header=header_html(L, "privacy.html"), h1=L["privacy_h1"],
        content=L["privacy_body"].strip(), home=home, back=L["back_home"],
        footer=footer_html(L, "privacy.html"))
    return page_shell(L, "privacy.html", L["privacy_title"],
                      L["privacy_h1"] + " — Scoperta", body, "")


def page_shell(L, page, title, desc, body, jsonld):
    return Template("""<!DOCTYPE html>
<html lang="${lang}" data-locale="${lang}">
<head>
${head}
${jsonld}
</head>
<body>
${body}
</body>
</html>
""").substitute(lang=L["lang"], head=head(L, page, title, desc),
                jsonld=jsonld, body=body)


def sitemap():
    pages = ["", "trip.html", "privacy.html"]
    urls = []
    for page in pages:
        alts = "\n".join(
            '    <xhtml:link rel="alternate" hreflang="%s" href="%s/%s%s"/>' % (lc, SITE, LOCALES[lc]["dir"], page)
            for lc in ORDER
        ) + '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s/en/%s"/>' % (SITE, page)
        for lc in ORDER:
            urls.append("  <url>\n    <loc>%s/%s%s</loc>\n%s\n  </url>" % (SITE, LOCALES[lc]["dir"], page, alts))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)


def main():
    for lc in ORDER:
        L = LOCALES[lc]
        write(L["dir"] + "index.html", index_page(L))
        write(L["dir"] + "trip.html", trip_page(L))
        write(L["dir"] + "privacy.html", privacy_page(L))
    write("sitemap.xml", sitemap())


if __name__ == "__main__":
    main()
