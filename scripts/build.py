"""Build the complete Crocevia Ricambi demo site (fictional business). Python standard library only; no external generator."""
from pathlib import Path
from html import escape
from urllib.parse import urlencode
import json
import os
import re
from hashlib import sha256
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("SITE_URL", "https://gxmich.github.io/crocevia-ricambi-demo").rstrip("/")
DEMO = True  # fictional business: always noindex
TEL = "+39 000 000 0000"
PHONE = "tel:+390000000000"
EMAIL = "info@crocevia-ricambi.example"
WA = "#whatsapp-demo"  # simulated: intercepted in site.js
PORTAL = "portale.html"  # simulated customer area
ADDRESS = "Via dei Mestieri 14, Rocca Tessera (Piemonte)"
MAP = "contatti.html#dove-siamo"
SIZES = json.loads((ROOT / "assets/image-sizes.json").read_text(encoding="utf-8"))
VARIANT_FILE = ROOT / "assets/image-variants.json"
VARIANTS = json.loads(VARIANT_FILE.read_text(encoding="utf-8")) if VARIANT_FILE.exists() else {}
PAGES = []
PARTNERS = ["Banco al pubblico", "Ricerca su targa e telaio", "Consegne in giornata", "Resi gestiti dal magazzino", "Ordini dal portale"]
BRANDS = ["Utilitarie", "Berline e station wagon", "SUV e crossover", "Veicoli commerciali", "Ibride", "Elettriche"]
FAMILIES = [
    {"slug": "manutenzione", "name": "Manutenzione", "link": "Ricambi di manutenzione", "image": "candela-wide", "detail": "filtro-olio-cut", "alt": "Candela di accensione", "lead": "Il tagliando e gli&nbsp;interventi di&nbsp;ogni&nbsp;giorno.", "text": "Filtri, freni, batterie e kit per il tagliando.", "intro": "Per un tagliando servono i componenti esatti per motorizzazione e versione. Mandaci targa o telaio: il magazzino individua i codici originali per quel veicolo e per quell'intervento.", "parts": ["Filtri olio, aria, abitacolo e carburante", "Dischi e pastiglie freno", "Batterie, candele e avviamento", "Lampadine", "Kit per il tagliando"], "gallery": [("disco-forato", "Disco freno"), ("candela-wide", "Candela di accensione")]},
    {"slug": "meccanica", "name": "Meccanica", "link": "Ricambi di meccanica", "image": "motore-cinghie-crop", "detail": None, "alt": "Cinghia e pulegge della distribuzione accessori di un motore", "lead": "Dal motore alle sospensioni.", "text": "Distribuzione, frizioni, sospensioni e scarico.", "intro": "Motorizzazione, versione e allestimento cambiano il componente. Con la targa o il codice del pezzo, il magazzino abbina il ricambio originale al veicolo che stai riparando.", "parts": ["Distribuzione e cinghie", "Frizioni e trasmissione", "Ammortizzatori e sospensioni", "Componenti motore", "Componenti di scarico", "Sterzo"], "gallery": [("motore", "Distribuzione di un motore"), ("catalizzatori", "Catalizzatori e componenti di scarico")]},
    {"slug": "carrozzeria", "name": "Carrozzeria", "link": "Ricambi di carrozzeria", "image": "specchietto", "detail": None, "alt": "Specchio retrovisore esterno di un'auto", "lead": "Ogni dettaglio torna al suo&nbsp;posto.", "text": "Paraurti, fari, specchi e lamierati.", "intro": "Per un particolare di carrozzeria contano lato di montaggio, versione e dotazioni. Indicaci il veicolo e il pezzo da sostituire: il magazzino individua il codice originale.", "parts": ["Paraurti e griglie", "Fari e fanali", "Specchi retrovisori", "Lamierati", "Cristalli e guarnizioni", "Minuteria di fissaggio"], "gallery": [("faro", "Gruppo ottico anteriore")]},
    {"slug": "accessori", "name": "Accessori", "link": "Accessori originali", "image": "tergicristallo-crop", "detail": None, "alt": "Spazzola tergicristallo sul parabrezza", "lead": "Gli originali che completano il&nbsp;veicolo.", "text": "Tergicristalli, accessori interni, liquidi e materiali di consumo.", "intro": "Dagli accessori per l'abitacolo ai materiali di consumo per l'officina: indica il modello del veicolo e cosa ti serve, il magazzino trova il codice originale compatibile.", "parts": ["Tergicristalli", "Tappeti e accessori interni", "Accessori per il trasporto", "Prodotti per la cura del veicolo", "Liquidi e lubrificanti", "Materiali di consumo"], "gallery": []},
]
# Framing for photographs shown with object-fit: cover (x y).
POSITIONS = {"specchietto": "40% 50%", "faro": "50% 62%"}


def icon(name="arrow"):
    paths = {
        "arrow": '<path d="M4 12h15m-6-6 6 6-6 6"/>',
        "external": '<path d="m6 18 12-12M7 6h11v11"/>',
        "phone": '<path d="m7 3 3 5-2 2a15 15 0 0 0 6 6l2-2 5 3-1 4C10 22 2 14 3 4Z"/>',
        "chat": '<path d="M20 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20l1.1-4.4A8.5 8.5 0 1 1 20 11.5Z"/><path d="M8 9h7M8 13h5"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
        "check": '<path d="m5 12 4 4L19 6"/>',
        "pin": '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
        "plus": '<path d="M12 5v14M5 12h14"/>',
    }
    return f'<svg class="icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def request(topic="Ricambi", category=""):
    values = {"tema": topic}
    if category:
        values["famiglia"] = category
    return "contatti.html?" + urlencode(values) + "#richiesta"


def button(label, href, style="primary", symbol="arrow", extra=""):
    external = href.startswith("https://")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    sr = '<span class="sr-only"> (si apre in una nuova scheda)</span>' if external else ""
    return f'<a class="button button-{style}" href="{escape(href, quote=True)}"{attrs} {extra}>{label}{icon(symbol)}{sr}</a>'


CHAR = re.compile(r'&[#\w]+;|.', re.S)
HEADING = re.compile(r'<(h[12])>(.*?)</\1>', re.S)


def compose(lines, classes=()):
    """Titles composed letter by letter: readable text for assistive tech, letters aria-hidden."""
    lines = [line.replace("'", "’") for line in lines]
    index = 0
    rendered = []
    for number, line in enumerate(lines):
        words = []
        for word in line.split():
            letters = []
            for char in CHAR.findall(word):
                letters.append(f'<span class="sc" style="--i:{index}">{char}</span>')
                index += 1
            words.append('<span class="sw">' + ''.join(letters) + '</span>')
        extra = f' {classes[number]}' if number < len(classes) and classes[number] else ''
        rendered.append(f'<span class="sl{extra}">' + ' '.join(words) + '</span>')
    readable = ' '.join(lines)
    return f'<span class="sr-only">{readable}</span><span class="split" aria-hidden="true">' + ''.join(rendered) + '</span>'


def compose_headings(html, levels=('h1', 'h2')):
    """Compose every plain h1/h2 (text and <br> only). Headings with attributes are left untouched."""
    def replace(match):
        tag, inner = match.group(1), match.group(2)
        if tag not in levels or '<' in inner.replace('<br>', ''):
            return match.group(0)
        return f'<{tag} data-compose>{compose([part.strip() for part in inner.split("<br>")])}</{tag}>'
    return HEADING.sub(replace, html)


@lru_cache(maxsize=None)
def asset_url(path):
    return path + '?v=' + sha256((ROOT / path).read_bytes()).hexdigest()[:10]


def picture(name, alt="", cls="", eager=False, sizes="(max-width: 700px) 100vw, 50vw", position=None):
    filename = name if "." in name else name + ".webp"
    w, h = SIZES[filename]
    variants = VARIANTS.get(filename, [])
    candidates = [f'{asset_url("img/" + variant["src"])} {variant["width"]}w' for variant in variants]
    if candidates:
        candidates.append(f'{asset_url("img/" + filename)} {w}w')
    srcset = f' srcset="{", ".join(candidates)}" sizes="{sizes}"' if candidates else ""
    loading = ' loading="eager"' if eager else ' loading="lazy"'
    if eager and filename == 'disco-forato-cut.webp':
        loading += ' fetchpriority="high"'
    position = position or POSITIONS.get(name)
    style = f' style="object-position:{position}"' if position else ""
    return f'<img src="{asset_url("img/" + filename)}" alt="{escape(alt, quote=True)}" width="{w}" height="{h}" class="{cls}"{style}{srcset}{loading} decoding="async">'


def cover_sizes(name, mobile, tablet, desktop):
    """sizes for a photo cropped with object-fit: cover. Each box is (width, height) in CSS px at 390, 768 and 1440."""
    w, h = SIZES[name if "." in name else name + ".webp"]
    width = lambda box: round(max(box[0], box[1] * w / h))
    return f'(max-width: 700px) {width(mobile)}px, (max-width: 900px) {width(tablet)}px, {width(desktop)}px'


def header(active):
    nav = [("ricambi", "ricambi.html", "Ricambi"), ("officine", "officine.html", "Per le officine"), ("azienda", "azienda.html", "Azienda"), ("contatti", "contatti.html", "Contatti")]
    links = "".join(f'<a href="{url}"' + (' aria-current="page"' if key == active else '') + f'>{label}</a>' for key, url, label in nav)
    return f'''<a class="skip-link" href="#contenuto">Vai al contenuto</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="index.html" aria-label="Crocevia Ricambi, magazzino ricambi a Rocca Tessera, pagina iniziale"><img class="brand-logo" src="img/logo-crocevia.svg" alt="Crocevia Ricambi" width="76" height="64"><span>Magazzino ricambi<br><span>Rocca Tessera</span></span></a>
<nav class="desktop-nav" aria-label="Navigazione principale">{links}</nav>
<div class="header-actions"><a class="header-phone" href="{PHONE}">{TEL}</a>{button('Portale clienti', PORTAL, 'outline')}<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-haspopup="dialog" aria-label="Apri il menu" hidden><span></span><span></span></button></div>
</div></header>
<div class="mobile-menu" id="mobile-menu" role="dialog" aria-modal="true" aria-label="Menu Crocevia Ricambi" hidden><nav aria-label="Navigazione mobile"><a href="index.html">Home</a>{links}</nav><div class="menu-contact"><p>Il magazzino, a portata di mano.</p><a href="{PHONE}">{TEL}</a>{button('Diventa cliente', request('Diventa cliente'), 'primary')}{button('Portale clienti', PORTAL, 'outline')}</div></div>
<noscript><nav class="no-script-nav" aria-label="Navigazione">{links}</nav></noscript>'''


def footer(active, anchored=False):
    families = "".join(f'<li><a href="famiglia-{f["slug"]}.html">{f["name"]}</a></li>' for f in FAMILIES)
    new_tab = '<span class="sr-only"> (si apre in una nuova scheda)</span>'
    # Contatti already shows call and WhatsApp next to the form: no fixed bar there.
    call = 'Chiama<span class="sr-only"> il magazzino</span>'
    dock = '' if active == 'contatti' else f'<nav class="mobile-dock" aria-label="Contatti rapidi"{" data-await" if anchored else ""}>{button(call, PHONE, "light", "phone")}{button("Richiedi un ricambio", request(), "primary")}</nav>'
    return f'''<footer class="site-footer"><div class="container footer-top"><a class="footer-brand" href="index.html" aria-label="Crocevia Ricambi, pagina iniziale"><img class="brand-logo" src="img/logo-crocevia.svg" alt="Crocevia Ricambi" width="94" height="78"></a><p>Ricambi originali per chi lavora sui veicoli, ogni&nbsp;giorno.</p></div>
<div class="container footer-grid"><div><h2>Ricambi</h2><ul>{families}</ul></div><div><h2>Per la tua officina</h2><ul><li><a href="officine.html">Servizi per le officine</a></li><li><a href="{request('Diventa cliente')}">Diventa cliente</a></li><li><a href="{PORTAL}">Portale clienti{icon()}</a></li><li><a href="azienda.html">L'azienda</a></li></ul></div><div><h2>Contatti</h2><ul><li><a href="{PHONE}">{TEL}</a></li><li><a href="{WA}">WhatsApp{icon()}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div><div><h2>Vieni a trovarci</h2><p>{ADDRESS}</p><a class="text-link" href="{MAP}">Indicazioni stradali {icon()}</a></div></div>
<div class="container footer-bottom"><p>© <span data-year>2026</span> Crocevia Ricambi · attività di fantasia</p><a href="privacy.html">Privacy e cookie</a><p>Sito dimostrativo</p></div><div class="container footer-demo"><p>Attività di fantasia: nomi, recapiti, prezzi e recensioni sono inventati. Sito dimostrativo realizzato da <a href="https://www.modicamichele.it">Michele Modica</a>.</p></div></footer>
{dock}'''


def page(filename, title, description, body, active="", css_class="", compose_levels=('h1', 'h2')):
    PAGES.append(filename)
    body = compose_headings(body, compose_levels)
    url = BASE + "/" + ("" if filename == "index.html" else filename)
    og_image = BASE + "/" + asset_url("assets/og.jpg")
    schema = {"@context": "https://schema.org", "@type": "AutoPartsStore", "name": "Crocevia Ricambi (attività di fantasia)", "url": BASE, "telephone": "+39 000 000 0000", "email": EMAIL, "address": {"@type": "PostalAddress", "streetAddress": "Via dei Mestieri 14", "addressLocality": "Rocca Tessera", "addressRegion": "Piemonte", "addressCountry": "IT"}, "areaServed": "Piemonte"}
    no_script = '<noscript><style>.mobile-dock{transform:none!important;visibility:visible!important}</style></noscript>'
    document = f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}"><meta name="robots" content="{'noindex, nofollow' if DEMO else 'index, follow'}"><meta name="theme-color" content="#0b0e13"><meta name="color-scheme" content="light dark">
<link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:locale" content="it_IT"><meta property="og:site_name" content="Crocevia Ricambi"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Crocevia Ricambi, ricambi per officine e carrozzerie (sito dimostrativo)"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="preload" href="assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{asset_url('assets/site.css')}">{no_script}<script src="{asset_url('assets/site.js')}" defer></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>
<body class="{css_class}">{header(active)}<main id="contenuto" tabindex="-1">{body}</main>{footer(active, 'data-dock-anchor' in body)}</body></html>'''
    (ROOT / filename).write_text(document + "\n", encoding="utf-8")


def breadcrumbs(current, parent=None):
    middle = f'<li><a href="{parent[0]}">{parent[1]}</a></li>' if parent else ""
    return f'<nav class="breadcrumbs" aria-label="Percorso di navigazione"><ol><li><a href="index.html">Home</a></li>{middle}<li aria-current="page">{current}</li></ol></nav>'


def cta(title="Il prossimo ricambio<br>parte da qui.", text="Targa, codice o solo la descrizione del pezzo: chiama, scrivi su WhatsApp o compila la richiesta. Al resto pensa il magazzino."):
    return f'<section class="contact-cta"><div class="container cta-grid"><div><h2>{title}</h2><p>{text}</p></div><div class="cta-actions">{button("Richiedi un ricambio", request(), "white") }<a class="cta-phone" href="{PHONE}"><span class="sr-only">Chiama il magazzino: </span>{TEL}</a><a class="cta-chat" href="{WA}">Scrivi su WhatsApp{icon()}</a></div></div></section>'


def family_cards(level=3):
    return '<div class="family-grid">' + "".join(f'<a class="family-item" href="famiglia-{f["slug"]}.html"><div class="family-image">{picture(f["image"], "", sizes=cover_sizes(f["image"], (123, 147), (217, 161), (268, 239)))}</div><div class="family-content"><h{level}>{f["name"]}</h{level}><p>{f["text"]}</p><span class="family-link">{f["link"]} {icon()}</span></div></a>' for f in FAMILIES) + '</div>'


def coverage():
    regions = ''.join(f'<li>{region}</li>' for region in ("Rocca Tessera", "Fondovalle", "Colline", "Pianura"))
    return f'''<section class="coverage section-light"><div class="container coverage-grid"><div><h2>Consegne in giornata<br>nelle zone servite.</h2><p>Dal magazzino di Rocca Tessera i ricambi raggiungono officine e carrozzerie del fondovalle, delle colline e della pianura.</p>{button("Consegne nella tua zona", request("Consegne e ritiro"), "dark")}</div><ul class="region-list" aria-label="Zone servite">{regions}</ul></div></section>'''


def faq():
    entries = [
        ("Non conosco il codice del ricambio. Posso chiedere lo stesso?", "Sì. Indica targa o telaio e descrivi il componente o l'intervento. Se non hai questi dati, aggiungi modello e motorizzazione: al codice pensa il magazzino."),
        ("Come inizio a lavorare con Crocevia?", f'Presentaci la tua officina con ragione sociale, comune e un recapito: il magazzino ti spiega come funziona il servizio e come accedere al portale. <a href="{request("Diventa cliente")}">Diventa cliente</a>.'),
        ("Le consegne arrivano nella mia zona?", "Il servizio copre Rocca Tessera e i paesi del fondovalle, delle colline e della pianura. Disponibilità e tempi dipendono dal singolo ordine: indica il comune dell'officina e il magazzino te li conferma prima di procedere."),
        ("Ho già un accesso: dove posso ordinare?", f'Nel <a href="{PORTAL}">portale clienti</a>. Per un problema di accesso, chiama il magazzino.'),
    ]
    return '<section class="faq section"><div class="container faq-grid"><div><h2>Prima di contattarci.</h2><p>Le informazioni utili per arrivare al ricambio giusto.</p></div><div class="faq-list">' + ''.join(f'<details><summary>{q}{icon("plus")}</summary><div class="faq-answer"><p>{a}</p></div></details>' for q, a in entries) + '</div></div></section>'


def home():
    title = f'<h1 class="hero-title" data-compose>{compose(["Il ricambio giusto.", "L’officina riparte."], ("", "accent"))}</h1>'
    tags = '<span class="part-tag tag-filter"><b>01</b>Filtro olio</span><span class="part-tag tag-disc"><b>02</b>Disco freno</span><span class="part-tag tag-plug"><b>03</b>Candela</span>'
    new_tab = '<span class="sr-only"> (si apre in una nuova scheda)</span>'
    hero = f'''<section class="hero"><div class="container hero-grid"><div class="hero-copy"><p class="hero-kicker">Magazzino ricambi · Rocca Tessera</p>{title}<p class="hero-description">Ricambi originali e di primo equipaggiamento per officine e carrozzerie. Mandaci targa o codice: il magazzino individua il pezzo e ti dà disponibilità e tempi di&nbsp;consegna.</p><div class="hero-actions" data-dock-anchor>{button("Richiedi un ricambio", request())}{button("Diventa cliente", request("Diventa cliente"), "outline")}</div><p class="hero-support">Hai già un accesso? <a href="{PORTAL}">Entra nel portale {icon()}</a></p></div><div class="hero-art" aria-hidden="true"><div class="part part-filter">{picture("filtro-olio-cut", eager=True, sizes="(max-width: 700px) 130px, (max-width: 900px) 220px, (max-width: 1100px) 18vw, 240px")}</div><div class="part part-disc">{picture("disco-forato-cut", eager=True, sizes="(max-width: 700px) 240px, (max-width: 900px) 380px, (max-width: 1100px) 34vw, 420px")}</div><div class="part part-plug">{picture("candela-cut", eager=True, sizes="(max-width: 700px) 36px, (max-width: 1100px) 5vw, 65px")}</div>{tags}</div></div><div class="container service-strip"><div><strong>Ricambi originali</strong><span>Per tutte le marche</span></div><a href="{request('Consegne e ritiro')}"><strong>Consegne giornaliere</strong><span>Chiedi per la tua zona {icon()}</span></a><a href="{PHONE}"><strong>Chiama il magazzino</strong><span>{TEL} {icon('phone')}</span></a></div></section>
<section class="brand-strip" aria-label="Veicoli seguiti"><div class="container"><p>Per ogni veicolo che entra in officina.</p><ul>{''.join(f'<li>{name}</li>' for name in BRANDS)}</ul></div></section>
<section class="section families"><div class="container"><div class="section-heading"><h2>Dalla manutenzione<br>alla carrozzeria.</h2><div><p>Quattro famiglie di ricambi originali. Hai già targa o codice? Richiedi direttamente il ricambio.</p><a class="text-link" href="ricambi.html">Indice dei ricambi {icon()}</a></div></div>{family_cards()}</div></section>
<section class="workshop-intro section-light"><div class="container workshop-grid"><div class="workshop-photo">{picture('meccanico', 'Meccanico al lavoro su un motore')}</div><div class="workshop-copy"><h2>Dalla targa al pezzo,<br>in tre passaggi.</h2><p>Un codice da controllare, un particolare da identificare, un tagliando da preparare: il magazzino parte dai dati del veicolo e ti indica il codice originale prima che il pezzo arrivi in officina.</p><ol class="process-list"><li><strong>Indica il veicolo</strong><span>Targa, telaio o modello e motorizzazione.</span></li><li><strong>Descrivi cosa ti serve</strong><span>Il componente, il codice se lo hai e la quantità.</span></li><li><strong>Ricevi codice e disponibilità</strong><span>Il magazzino ti risponde con il codice originale, la disponibilità e i tempi di consegna.</span></li></ol>{button('Richiedi un ricambio', request(), 'dark')}</div></div></section>
<section class="portal-section section"><div class="container portal-grid"><div><h2>Ordini e documenti<br>nel portale clienti.</h2><p>Sei già cliente? Dal portale accedi al catalogo del tuo profilo, agli ordini web e ai documenti.</p><div class="button-row">{button('Apri il portale clienti', PORTAL, 'primary')}<a class="text-link" href="{request('Accesso al portale')}">Ti serve un accesso? {icon()}</a></div></div><div class="portal-index"><a href="{PORTAL}"><span>Ordini web</span><span>Il catalogo del tuo profilo</span>{icon()}</a><a href="{PORTAL}"><span>Documenti</span><span>Fatture e documenti di trasporto</span>{icon()}</a><a href="{request('Diventa cliente')}"><span>Nuova officina?</span><span>Diventa cliente</span>{icon()}</a></div></div></section>
<section class="company-preview section section-light"><div class="container company-grid"><div><h2>Un banco ricambi cresciuto accanto alle&nbsp;officine.</h2><p>Chi lavora al banco ha passato anni tra cataloghi, versioni e codici. Oggi quell'esperienza serve a chi ripara veicoli ogni giorno.</p><a class="text-link" href="azienda.html">Conosci Crocevia Ricambi {icon()}</a><ul class="partner-list">{''.join(f'<li>{name}</li>' for name in PARTNERS)}</ul></div><figure>{picture('struttura', 'Il capannone del magazzino Crocevia Ricambi')}<figcaption>Il magazzino in Via dei Mestieri, a Rocca Tessera.</figcaption></figure></div></section>
<section class="workshop-link section"><div class="container"><div><h2>Supporto tecnico, formazione e rete di officine.</h2><p>Oltre ai ricambi: dicci cosa ti serve e ti spieghiamo cosa è attivo per la tua officina.</p></div>{button('Servizi per le officine', 'officine.html', 'outline')}</div></section>
{faq()}{cta()}'''
    page('index.html', 'Crocevia Ricambi | Ricambi per officine e carrozzerie', 'Ricambi originali e di primo equipaggiamento per officine e carrozzerie. Mandaci targa o codice: il magazzino Crocevia di Rocca Tessera individua il pezzo e ti dà disponibilità e tempi di consegna.', hero, 'home', 'page-home')


def ricambi():
    items = ''.join(f'<li class="index-item"><span class="index-number" aria-hidden="true">{number:02d}</span><div class="index-head"><h2>{f["name"]}</h2><p>{f["text"]}</p></div><ul class="index-parts">{"".join(f"<li>{part}</li>" for part in f["parts"])}</ul><a class="text-link index-link" href="famiglia-{f["slug"]}.html">{f["link"]} {icon()}</a></li>' for number, f in enumerate(FAMILIES, 1))
    steps = '<ol class="process-list"><li><strong>Targa o telaio</strong><span>Identificano la versione esatta del veicolo.</span></li><li><strong>Componente e quantità</strong><span>Descrivi il pezzo o l’intervento e aggiungi il codice, se lo hai.</span></li><li><strong>Il canale che preferisci</strong><span>Telefono, WhatsApp o la richiesta dal sito.</span></li></ol>'
    body = f'''<section class="page-heading container">{breadcrumbs("Ricambi")}<div class="heading-grid"><h1>Quattro famiglie di<br>ricambi originali.</h1><div><p class="lead">Manutenzione, meccanica, carrozzeria e accessori per auto e veicoli commerciali di tutte le marche. Per ogni famiglia trovi le tipologie che puoi richiedere al magazzino.</p><div data-dock-anchor>{button("Richiedi un ricambio", request())}</div></div></div></section>
<section class="parts-index" aria-label="Indice delle famiglie di ricambi"><div class="container"><ol class="index-list">{items}</ol></div></section>
<section class="brands-section"><div class="container brands-grid"><h2>Tutte le marche,<br>ogni tipo di veicolo.</h2><div><p>Ricambi originali e di primo equipaggiamento per questi veicoli.</p><ul class="brands-list">{''.join(f'<li>{name}</li>' for name in BRANDS)}</ul></div></div></section>
<section class="how-to section-light"><div class="container how-to-grid"><div><h2>Come chiedere<br>un ricambio.</h2><p>Lo stesso modello può montare componenti diversi: per questo partiamo dal veicolo.</p></div>{steps}</div></section>{cta()}'''
    page('ricambi.html', 'Indice dei ricambi | Crocevia Ricambi', 'Indice dei ricambi Crocevia: manutenzione, meccanica, carrozzeria e accessori per tutte le marche, con le tipologie disponibili e come chiedere un ricambio.', body, 'ricambi', 'page-parts')


def famiglia(f):
    if f['detail']:
        visual = picture(f['detail'], '', 'category-cut', eager=True)
    else:
        visual = picture(f['image'], f['alt'], eager=True, sizes=cover_sizes(f['image'], (350, 241), (316, 316), (599, 479)))
    related = ''.join(f'<a href="famiglia-{other["slug"]}.html">{other["name"]}{icon()}</a>' for other in FAMILIES if other != f)
    request_block = f'''<div class="category-request"><h2>Partiamo dal veicolo.</h2><p>Indica targa o telaio, il componente da sostituire e la quantità. Se hai il codice del pezzo, aggiungilo alla richiesta.</p>{button('Richiedi un ricambio', request('Ricambi', f['name']))}</div>'''
    gallery = f['gallery']
    if len(gallery) > 1:
        figures = ''.join(f'<figure>{picture(name, alt, sizes=cover_sizes(name, (169, 169), (338, 260), (648, 498)))}<figcaption>{alt}</figcaption></figure>' for name, alt in gallery)
        detail = f'<div class="detail-gallery">{figures}</div>{request_block}'
    elif gallery:
        name, alt = gallery[0]
        detail = f'<div class="detail-pair"><figure>{picture(name, alt, sizes=cover_sizes(name, (350, 269), (330, 300), (615, 559)))}<figcaption>{alt}</figcaption></figure>{request_block}</div>'
    else:
        detail = request_block.replace('category-request', 'category-request is-solo', 1)
    body = f'''<section class="container category-hero">{breadcrumbs(f['name'], ('ricambi.html', 'Ricambi'))}<div class="category-grid"><div><h1>{f['name']}</h1><p class="category-lead">{f['lead']}</p><p>{f['intro']}</p><div class="button-row" data-dock-anchor>{button('Richiedi un ricambio', request('Ricambi', f['name']))}<a class="text-link" href="{PHONE}">Chiama il magazzino {icon('phone')}</a></div></div><div class="category-visual">{visual}</div></div></section>
<section class="parts-section section-light"><div class="container parts-grid"><div><h2>Per il tuo<br>prossimo intervento.</h2><p>Alcune delle tipologie che puoi richiedere al magazzino.</p></div><ul class="parts-list">{''.join(f'<li>{icon("check")}<span>{part}</span></li>' for part in f['parts'])}</ul></div></section>
<section class="section"><div class="container">{detail}</div></section>
<section class="related-section container"><h2 class="related-title">Le altre famiglie</h2><div>{related}</div></section>{cta()}'''
    page(f'famiglia-{f["slug"]}.html', f'Ricambi {f["name"].lower()} originali | Crocevia Ricambi', f'{f["text"]} Ricambi originali e di primo equipaggiamento per officine e carrozzerie: chiedili al magazzino Crocevia di Rocca Tessera.', body, 'ricambi', 'page-category')


def officine():
    new_tab = '<span class="sr-only"> (si apre in una nuova scheda)</span>'
    body = f'''<section class="container page-heading">{breadcrumbs('Per le officine')}<div class="editorial-hero"><div><h1>Il magazzino per officine e&nbsp;carrozzerie.</h1><p class="lead">Ricambi originali e di primo equipaggiamento, un magazzino che individua con te il codice giusto, consegne giornaliere nelle zone servite e un portale per ordinare online.</p><div class="button-row" data-dock-anchor>{button('Diventa cliente', request('Diventa cliente'))}<a class="text-link" href="{PHONE}">Chiama il magazzino {icon('phone')}</a></div></div><figure>{picture('officina', 'Un veicolo durante un intervento in officina', eager=True, sizes='(max-width: 700px) 404px, (max-width: 900px) 498px, 922px')}</figure></div></section>
<section class="section service-editorial"><div class="container"><h2>Ricambi, consegne<br>e portale clienti.</h2><div class="service-rows"><article><h3>Ricambi originali</h3><p>Parti dalla targa o dal codice: il magazzino individua il componente originale per l'intervento.</p><a class="text-link" href="{request()}">Richiedi un ricambio {icon()}</a></article><article><h3>Consegne giornaliere</h3><p>Nei paesi intorno a Rocca Tessera, con due giri di consegna al giorno.</p><a class="text-link" href="{request('Consegne e ritiro')}">Consegne nella tua zona {icon()}</a></article><article><h3>Portale clienti</h3><p>Ordini web, fatture e documenti di trasporto nel profilo della tua officina.</p><a class="text-link" href="{PORTAL}">Apri il portale clienti {icon()}</a></article></div></div></section>
<section class="new-customer section-light" id="diventa-cliente"><div class="container parts-grid"><div><h2>Diventa cliente<br>in tre passaggi.</h2><p>Cerchi un fornitore di ricambi originali? Presentaci la tua officina: ti spieghiamo come funziona il servizio Crocevia e come accedere al portale.</p>{button('Diventa cliente', request('Diventa cliente'), 'dark')}</div><ol class="process-list"><li><strong>Presenta la tua officina</strong><span>Ragione sociale, comune e un recapito.</span></li><li><strong>Conosci il servizio</strong><span>Il magazzino ti spiega consegne e modalità per la tua zona.</span></li><li><strong>Chiedi l'accesso al portale</strong><span>Concorda attivazione e servizi del tuo profilo.</span></li></ol></div></section>
<section class="section services-more" id="rete"><div class="container more-grid"><div><h2>Supporto tecnico, formazione e rete di officine.</h2><p class="lead">Dicci cosa ti serve: ti spieghiamo cosa è attivo per la tua officina.</p><div class="button-row">{button('Chiedi informazioni', request('Supporto e formazione'))}<a class="text-link" href="{request('Rete officine')}">Rete Officine Crocevia {icon()}</a></div></div><ul class="more-list"><li><strong>Supporto tecnico</strong><span>Un dubbio su un componente o su un intervento.</span></li><li><strong>Formazione</strong><span>Aggiornamento tecnico per chi lavora in officina.</span></li><li><strong>Rete Officine Crocevia</strong><span>Un'insegna comune e servizi condivisi per le officine indipendenti della zona.</span></li></ul></div></section>{cta()}'''
    page('officine.html', 'Servizi per officine e nuovi clienti | Crocevia Ricambi', 'Ricambi originali, consegne in giornata nelle zone servite, portale clienti, supporto tecnico, formazione e rete di officine. Diventa cliente di Crocevia Ricambi.', body, 'officine', 'page-workshops')


def azienda():
    body = f'''<section class="container page-heading">{breadcrumbs('Azienda')}<div class="editorial-hero"><div><h1>Il magazzino ricambi di Rocca Tessera.</h1><p class="lead">Crocevia Ricambi lavora per officine e carrozzerie: ricambi originali e di primo equipaggiamento, ricerca del codice sul veicolo e un contatto diretto con chi sta al banco.</p><div class="button-row" data-dock-anchor>{button('Chiama il magazzino', PHONE, 'primary', 'phone')}</div></div><figure>{picture('sede', 'Corsie e scaffali del magazzino ricambi', eager=True, sizes='(max-width: 700px) 100vw, 50vw')}<figcaption>Via dei Mestieri 14 · Rocca Tessera</figcaption></figure></div></section>
<section class="section company-story"><div class="container parts-grid"><h2>Nato al banco, per chi ripara.</h2><div><p class="lead">Chi lavora da Crocevia conosce i veicoli dal lato del banco ricambi: modelli, versioni, codici.</p><p>Questa esperienza oggi lavora per chi ripara veicoli ogni giorno, dalla ricerca del pezzo alla consegna in officina.</p><ul class="partner-list">{''.join(f'<li>{name}</li>' for name in PARTNERS)}</ul></div></div></section>
<figure class="wide-photo container">{picture('struttura', 'Il capannone del magazzino', sizes='(max-width: 1448px) 92vw, 1320px')}<figcaption>Il nostro magazzino a Rocca Tessera.</figcaption></figure>{coverage()}
<section class="section company-visit"><div class="container heading-grid"><h2>Il magazzino è<br>a Rocca Tessera.</h2><div><p class="lead">{ADDRESS}</p><p>Per un ricambio, una consegna o una nuova collaborazione, il primo passo è una telefonata al magazzino.</p><div class="button-row">{button('Come raggiungerci', MAP, 'primary', 'pin')}{button('Chiama il magazzino', PHONE, 'outline', 'phone')}</div></div></div></section>{cta()}'''
    page('azienda.html', 'Azienda | Crocevia Ricambi', 'Crocevia Ricambi, magazzino di ricambi per officine e carrozzerie a Rocca Tessera: chi siamo, dove siamo e quali zone serviamo.', body, 'azienda', 'page-company')


def field(name, label, kind="text", placeholder="", autocomplete="", required=False, error="", extra=""):
    aid = f"field-{name}"
    attributes = f' type="{kind}" name="{name}" id="{aid}" maxlength="180"'
    if placeholder:
        attributes += f' placeholder="{placeholder}"'
    if autocomplete:
        attributes += f' autocomplete="{autocomplete}"'
    if required:
        attributes += ' required'
    attributes += f' aria-describedby="error-{name}" {extra}'
    return f'<div class="field"><label for="{aid}">{label}{" <span aria-hidden=\"true\">*</span>" if required else ""}</label><input{attributes}><small class="field-error" id="error-{name}" hidden>{error}</small></div>'


def contatti():
    topics = ["Ricambi", "Diventa cliente", "Accesso al portale", "Consegne e ritiro", "Supporto e formazione", "Rete officine", "Altre informazioni"]
    new_tab = '<span class="sr-only"> (si apre in una nuova scheda)</span>'
    form = f'''<div class="request-panel" id="richiesta"><form data-request-form hidden novalidate><div class="form-header"><h2 data-form-title>Prepara la richiesta</h2><p>Compila i dati utili, poi scegli WhatsApp o email.</p></div><div class="form-error-summary" role="alert" tabindex="-1" hidden data-errors></div><div data-form-fields><div class="field"><label for="field-tema">Di cosa hai bisogno?</label><select name="tema" id="field-tema">{''.join(f'<option>{topic}</option>' for topic in topics)}</select></div><input type="hidden" name="famiglia" data-category><p class="category-context" data-category-context hidden></p>
<fieldset class="form-vehicle" data-topics="Ricambi"><legend>Il veicolo e il ricambio</legend><div class="form-row">{field('targa', 'Targa o telaio', placeholder='Es. AB123CD', extra='autocapitalize="characters" spellcheck="false"')}{field('codice', 'Codice ricambio', placeholder='Se lo conosci')}</div></fieldset>
<div class="field"><label for="field-desc" data-description-label>Che ricambio ti serve? <span aria-hidden="true">*</span></label><textarea name="desc" id="field-desc" rows="3" maxlength="1800" required aria-describedby="description-help error-desc" placeholder="Descrivi il componente, la quantità e l'intervento."></textarea><small id="description-help" data-description-help>Se non hai targa o codice, indica modello e motorizzazione.</small><small class="field-error" id="error-desc" hidden>Descrivi brevemente ciò di cui hai bisogno.</small></div>
<div class="form-row">{field('nome', 'Il tuo nome', autocomplete='name', required=True, error='Inserisci il tuo nome.')}{field('azienda', 'Officina o azienda', autocomplete='organization')}</div>
<fieldset data-topics="Diventa cliente|Consegne e ritiro|Rete officine"><legend>La tua zona</legend>{field('comune', "Comune dell'officina", placeholder='Comune e provincia', autocomplete='address-level2')}</fieldset>
<fieldset class="contact-fields"><legend>Come possiamo ricontattarti?</legend><p class="field-help" id="contact-help">Lascia almeno un numero di telefono o un'email.</p><div class="form-row">{field('tel', 'Telefono', kind='tel', autocomplete='tel', error='Inserisci un telefono valido oppure un indirizzo email.', extra='aria-required="false"')}{field('email', 'Email', kind='email', autocomplete='email', error="Controlla l'indirizzo email.")}</div></fieldset>
<p class="form-privacy">I tuoi dati servono solo a rispondere alla richiesta. I campi con * sono obbligatori. <a href="privacy.html">Leggi l'informativa privacy</a></p><button class="button button-primary form-submit" type="submit">Prepara il messaggio {icon()}</button><p class="form-hint">Potrai rivederlo prima di aprire WhatsApp o email.</p></div>
<section class="request-review" data-review hidden tabindex="-1" aria-labelledby="review-title"><div class="review-symbol">{icon('check')}</div><h2 id="review-title">Il messaggio è pronto.</h2><p>Controlla il riepilogo. In un sito vero apriresti WhatsApp o la tua email per inviarlo: in questa demo i pulsanti non aprono nulla e non inviano dati.</p><dl data-review-list></dl><div class="review-actions"><a class="button button-primary" data-send-wa href="#whatsapp-demo">Apri WhatsApp {icon('chat')}</a><a class="button button-dark" data-send-email href="#email-demo">Apri la tua email {icon('mail')}</a></div><button class="text-link edit-request" type="button" data-edit-request>Modifica la richiesta</button></section></form><noscript><div class="no-script-request"><h2 class="no-script-title">Contatta direttamente il magazzino</h2><p>Indica veicolo, ricambio e recapito nel tuo messaggio.</p>{button('Scrivi su WhatsApp', WA, 'primary', 'chat')}{button('Scrivi una email', 'mailto:' + EMAIL, 'dark', 'mail')}</div></noscript></div>'''
    body = f'''<div class="container">{breadcrumbs('Contatti')}<section class="contact-layout"><div class="contact-intro"><h1 data-contact-title data-compose>{compose(["Il ricambio", "che ti serve."])}</h1><p class="lead" data-contact-lead>Targa, codice o una semplice descrizione: compila la richiesta e inviala al magazzino su WhatsApp o via email.</p><div class="contact-shortcuts">{button('Chiama il magazzino', PHONE, 'outline', 'phone')}{button('Scrivi su WhatsApp', WA, 'outline', 'chat')}</div><div class="contact-directory"><div><h2 class="directory-label">Il magazzino</h2><a class="contact-number" href="{PHONE}"><span class="sr-only">Chiama il magazzino: </span>{TEL}</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{WA}">WhatsApp: +39 000 000 0000{icon()}</a></div><div><h2 class="directory-label">Sei già cliente?</h2><p>Ordini e documenti del tuo profilo sono nel portale.</p><a class="text-link" href="{PORTAL}">Apri il portale clienti {icon()}</a></div></div></div>{form}</section></div>
<section class="visit-section section-light" id="dove-siamo"><div class="container visit-grid"><div><h2>Ci trovi<br>a Rocca Tessera.</h2><p>{ADDRESS}</p><p>Per un ritiro al banco, chiama il magazzino prima di partire.</p></div><figure>{picture('struttura', 'Il capannone del magazzino Crocevia Ricambi')}</figure></div></section>'''
    page('contatti.html', 'Contatti e richieste ricambi | Crocevia Ricambi', 'Prepara una richiesta di ricambi per il magazzino Crocevia: modulo dimostrativo, nessun dato viene inviato.', body, 'contatti', 'page-contact')


def privacy():
    body = f'''<section class="container legal-page">{breadcrumbs('Privacy e cookie')}<h1>Privacy e cookie</h1><p class="legal-note">Informativa dimostrativa: l'attività è di fantasia e questo sito non raccoglie dati.</p><div class="legal-content">
<p class="legal-intro">Questa informativa spiega come Crocevia Ricambi tratta i dati di chi visita il sito e di chi ci contatta, ai sensi del Regolamento UE 2016/679 (GDPR).</p>
<h2>Titolare del trattamento</h2><p>Crocevia Ricambi (attività di fantasia), {ADDRESS}. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Quali dati trattiamo</h2><p>Dati di navigazione: i registri tecnici che il servizio di hosting conserva per il funzionamento e la sicurezza del sito.</p><p>Dati che ci invii: nome, recapiti, officina o azienda, comune, dati del veicolo e contenuto della richiesta, quando scegli di scriverci.</p>
<h2>Come funziona il modulo di richiesta</h2><p>Il modulo compone il messaggio nel tuo browser: il sito non invia e non archivia i dati inseriti. Rivedi il riepilogo e scegli se aprire WhatsApp o il tuo programma email, dove completi tu l'invio. Inserisci solo le informazioni utili alla richiesta.</p>
<h2>Finalità e base giuridica</h2><p>Usiamo i dati per rispondere alle richieste e per le misure precontrattuali che ci chiedi (art. 6.1.b GDPR). I registri tecnici servono al funzionamento e alla sicurezza del sito (legittimo interesse, art. 6.1.f GDPR). Non usiamo i dati per newsletter o comunicazioni di marketing.</p>
<h2>Conservazione e destinatari</h2><p>Conserviamo i dati per il tempo necessario a gestire la richiesta e l'eventuale rapporto commerciale, e per gli obblighi di legge. I fornitori dei servizi di hosting e di posta elettronica possono trattarli per conto di Crocevia Ricambi, solo per queste finalità.</p>
<h2>Cookie e servizi esterni</h2><p>Il sito non usa cookie, strumenti di analisi del traffico, pixel pubblicitari o mappe incorporate e non salva dati nel browser. I caratteri tipografici sono ospitati sul sito stesso.</p><p>In questa demo i collegamenti a WhatsApp, email e telefono sono simulati e non aprono servizi esterni.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere l'accesso ai tuoi dati, la rettifica, la cancellazione, la limitazione del trattamento, la portabilità e opporti al trattamento, scrivendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. Puoi anche proporre reclamo al Garante per la protezione dei dati personali.</p>
<p class="legal-date">Ultimo aggiornamento: novembre 2026.</p></div></section>'''
    page('privacy.html', 'Privacy e cookie | Crocevia Ricambi', 'Informativa privacy e cookie di Crocevia Ricambi (attività di fantasia): dati trattati, richieste via WhatsApp o email, cookie e diritti degli interessati.', body, '', 'page-legal', compose_levels=('h1',))


def portale():
    body = f'''<section class="container page-heading">{breadcrumbs('Portale clienti')}<div class="heading-grid"><h1>Il portale<br>clienti.</h1><div><p class="lead">Ordini web, fatture e documenti di trasporto nel profilo della tua officina.</p><p>In questa demo il portale è una pagina d'esempio: l'accesso non è attivo e i campi sono disabilitati.</p><form class="request-panel portal-demo" aria-label="Accesso al portale, dimostrativo" onsubmit="return false"><div class="field"><label for="portal-user">Codice cliente</label><input id="portal-user" type="text" disabled placeholder="Es. OFF-0000"></div><div class="field"><label for="portal-pass">Password</label><input id="portal-pass" type="password" disabled></div><button class="button button-primary" type="button" disabled>Entra nel portale</button><p class="portal-note">Accesso simulato: nessun dato viene inviato.</p></form><div class="button-row">{button('Chiedi un accesso', request('Accesso al portale'), 'outline')}</div></div></div></section>{cta()}'''
    page('portale.html', 'Portale clienti | Crocevia Ricambi', 'Area clienti dimostrativa di Crocevia Ricambi: ordini, fatture e documenti di trasporto. Accesso non attivo.', body, '', 'page-portal', compose_levels=('h1',))


def main():
    home()
    ricambi()
    for family in FAMILIES:
        famiglia(family)
    officine()
    azienda()
    contatti()
    privacy()
    portale()
    urls = ''.join(f'  <url><loc>{BASE}/{"" if filename == "index.html" else filename}</loc></url>\n' for filename in PAGES)
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n', encoding='utf-8')
    robots = 'User-agent: *\nDisallow: /\n' if DEMO else f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n'
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')
    print(f'Built {len(PAGES)} pages. Mode: {"demo, noindex" if DEMO else "production"}.')


if __name__ == '__main__':
    main()
