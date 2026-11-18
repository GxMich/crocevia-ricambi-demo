# Crocevia Ricambi — sito dimostrativo

**Demo online → https://gxmich.github.io/crocevia-ricambi-demo/**

> ### Attività di fantasia
>
> **Crocevia Ricambi non esiste.** Nome, logo, indirizzo (Rocca Tessera è un paese inventato), telefono,
> email, zone servite e storia sono inventati e servono solo a mostrare come funziona il sito.
>
> L'email usa il dominio `crocevia-ricambi.example`: `.example` è riservato dallo IANA e non può
> recapitare posta. Il telefono è `+39 000 000 0000`.
>
> Il modulo di richiesta, i pulsanti WhatsApp ed email e il portale clienti sono **simulati**:
> non inviano dati a nessuno e non aprono app esterne.
>
> Tutte le pagine hanno `<meta name="robots" content="noindex, nofollow">` e `robots.txt` blocca
> l'intero sito. Su un project site di GitHub Pages il `robots.txt` in sottocartella non viene letto:
> la protezione effettiva è il `noindex` nelle pagine.

Sito di un magazzino ricambi auto che lavora con officine e carrozzerie. Undici pagine statiche in
HTML, CSS e JavaScript, senza framework e senza librerie esterne: font e immagini sono nel progetto.

## Cosa mostra la demo

- **Home** con ricambi scontornati e numerati nel hero, titoli composti lettera per lettera e i due
  percorsi principali: chiedere un ricambio o diventare cliente.
- **Indice dei ricambi** e quattro pagine di famiglia (manutenzione, meccanica, carrozzeria,
  accessori), ognuna con le tipologie richiedibili e una richiesta già precompilata.
- **Per le officine**: servizi, come diventare cliente in tre passaggi, supporto e rete di officine.
- **Contatti** con una richiesta guidata: il modulo cambia campi e testi in base al tema
  (ricambio, nuovo cliente, consegne, portale…), controlla i dati e mostra un riepilogo.
  Da lì i pulsanti WhatsApp ed email mostrano solo un avviso: niente viene inviato.
- **Portale clienti** d'esempio, con accesso disattivato.
- Barra rapida su telefono (chiamata e richiesta) che compare quando i pulsanti principali escono
  dallo schermo, menu mobile accessibile, rispetto di «riduci movimento».

## Tecnologie

- HTML generato da `scripts/build.py` (solo libreria standard di Python): contenuti e componenti
  condivisi stanno lì; stili in `assets/site.css`, comportamenti in `assets/site.js`.
- Font Archivo e Inter ospitati nel progetto (licenza SIL OFL, vedi `assets/fonts/`).
- Immagini WebP con varianti responsive (`img/responsive/`, elencate in `assets/image-variants.json`).
- Pubblicazione su GitHub Pages direttamente dal ramo `main`.

## Avviarla in locale

```bash
python scripts/build.py          # rigenera le pagine (facoltativo: le pagine sono già nel repository)
python -m http.server 8000
```

Poi apri http://127.0.0.1:8000/.

## Crediti

Foto da Unsplash, elencate in [CREDITI-FOTO.md](CREDITI-FOTO.md). Sito dimostrativo realizzato da
[Michele Modica](https://www.modicamichele.it).
