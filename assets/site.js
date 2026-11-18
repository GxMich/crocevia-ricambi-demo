/* Crocevia Ricambi (demo): composed titles, navigation and a local, reviewable request. No tracking or automatic sending. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  $$('[data-year]').forEach(element => { element.textContent = String(new Date().getFullYear()); });

  /* Titles composed letter by letter. Readable text stays in a visually hidden span. */
  function composeTitle(element, text) {
    const lines = text.replace(/'/g, '’').split('\n');
    const readable = document.createElement('span');
    readable.className = 'sr-only';
    readable.textContent = lines.join(' ');
    const split = document.createElement('span');
    split.className = 'split';
    split.setAttribute('aria-hidden', 'true');
    let index = 0;
    lines.forEach(line => {
      const row = document.createElement('span');
      row.className = 'sl';
      line.split(/\s+/).filter(Boolean).forEach((word, position) => {
        if (position) row.append(' ');
        const group = document.createElement('span');
        group.className = 'sw';
        [...word].forEach(character => {
          const letter = document.createElement('span');
          letter.className = 'sc';
          letter.style.setProperty('--i', String(index++));
          letter.textContent = character;
          group.append(letter);
        });
        row.append(group);
      });
      split.append(row);
    });
    element.replaceChildren(readable, split);
  }

  const sectionTitles = $$('h2[data-compose]');
  if (sectionTitles.length && 'IntersectionObserver' in window && !reduceMotion.matches) {
    const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      reveal.unobserve(entry.target);
    }), { rootMargin: '0px 0px -8% 0px' });
    sectionTitles.forEach(title => {
      const box = title.getBoundingClientRect();
      if (box.top < window.innerHeight && box.bottom > 0) title.classList.add('is-shown');
      else reveal.observe(title);
    });
    document.documentElement.classList.add('compose-ready');
    window.addEventListener('beforeprint', () => sectionTitles.forEach(title => title.classList.add('is-in')));
  }

  /* Hero parts follow the pointer by a few pixels on desktop only. */
  const hero = $('.hero');
  const art = $('.hero-art');
  if (hero && art && window.matchMedia('(hover: hover) and (pointer: fine)').matches && !reduceMotion.matches) {
    let frame = 0;
    let pointer = [0, 0];
    hero.addEventListener('pointermove', event => {
      pointer = [event.clientX, event.clientY];
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        const box = hero.getBoundingClientRect();
        art.style.setProperty('--mx', ((pointer[0] - box.left) / box.width * 2 - 1).toFixed(3));
        art.style.setProperty('--my', ((pointer[1] - box.top) / box.height * 2 - 1).toFixed(3));
      });
    });
    hero.addEventListener('pointerleave', () => {
      art.style.setProperty('--mx', '0');
      art.style.setProperty('--my', '0');
    });
  }

  /* Mobile bar: on pages with an opening call to action, it appears once that action has left the screen. */
  const dockAnchor = $('[data-dock-anchor]');
  const waitingDock = $('.mobile-dock[data-await]');
  if (waitingDock) {
    if (dockAnchor && 'IntersectionObserver' in window) {
      new IntersectionObserver(entries => entries.forEach(entry => {
        waitingDock.classList.toggle('is-visible', !entry.isIntersecting);
      })).observe(dockAnchor);
    } else {
      waitingDock.classList.add('is-visible');
    }
  }

  const toggle = $('.menu-toggle');
  const menu = $('#mobile-menu');
  const main = $('main');
  const footer = $('.site-footer');
  const dock = $('.mobile-dock');
  const compactNav = window.matchMedia('(max-width: 1100px)');
  let previousFocus = null;

  function setMenu(open, restore = true) {
    if (!toggle || !menu) return;
    if (open) previousFocus = document.activeElement;
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Chiudi il menu' : 'Apri il menu');
    document.body.classList.toggle('menu-open', open);
    [main, footer, dock, $('.skip-link')].forEach(element => { if (element) element.inert = open; });
    if (open) $('a', menu)?.focus({ preventScroll: true });
    else if (restore) (previousFocus || toggle).focus({ preventScroll: true });
  }

  if (toggle && menu) {
    toggle.hidden = !compactNav.matches;
    toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
    menu.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false, false); });
    compactNav.addEventListener('change', event => {
      if (!event.matches && !menu.hidden) {
        setMenu(false, false);
        $('.brand')?.focus({ preventScroll: true });
      }
      toggle.hidden = !event.matches;
    });
    document.addEventListener('keydown', event => {
      if (menu.hidden) return;
      if (event.key === 'Escape') { event.preventDefault(); setMenu(false); }
      if (event.key === 'Tab') {
        const targets = [toggle, ...$$('a[href], button:not([disabled])', menu)];
        const first = targets[0];
        const last = targets.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
  }

  const form = $('[data-request-form]');
  if (!form) return;
  const fields = $('[data-form-fields]', form);
  const review = $('[data-review]', form);
  const errorSummary = $('[data-errors]', form);
  const topic = $('#field-tema', form);
  const heading = $('[data-form-title]', form);
  const description = $('#field-desc', form);
  const descriptionLabel = $('[data-description-label]', form);
  const descriptionHelp = $('[data-description-help]', form);
  const category = $('[data-category]', form);
  const categoryContext = $('[data-category-context]', form);
  const params = new URLSearchParams(window.location.search);
  const allowedTopics = [...topic.options].map(option => option.value);
  const allowedCategories = ['Manutenzione', 'Meccanica', 'Carrozzeria', 'Accessori'];
  const topicCopy = {
    'Ricambi': {
      title: 'Prepara la richiesta',
      label: 'Che ricambio ti serve?',
      hint: 'Se non hai targa o codice, indica modello e motorizzazione.',
      placeholder: "Descrivi il componente, la quantità e l'intervento.",
      pageTitle: 'Il ricambio\nche ti serve.',
      lead: 'Targa, codice o una semplice descrizione: compila la richiesta e inviala al magazzino su WhatsApp o via email.'
    },
    'Diventa cliente': {
      title: 'Presentaci la tua officina',
      label: 'Come possiamo aiutare la tua officina?',
      hint: 'Indica il tipo di attività e i servizi che ti interessano.',
      placeholder: 'Es. officina meccanica in paese, interessata a ricambi e consegne.',
      pageTitle: 'Lavoriamo\ninsieme.',
      lead: 'Presentaci la tua attività: parliamo di ricambi, consegne nella tua zona e accesso al portale clienti.'
    },
    'Accesso al portale': {
      title: "Parliamo dell'accesso", label: 'Di quale aiuto hai bisogno?',
      hint: 'Non inserire password o credenziali nel messaggio.',
      placeholder: 'Es. vorrei attivare un profilo per la mia officina.',
      pageTitle: 'Il tuo accesso\nal portale.',
      lead: 'Per una nuova abilitazione o un dubbio sul profilo, prepara una richiesta per il magazzino.'
    },
    'Consegne e ritiro': {
      title: 'Consegne nella tua zona', label: 'Di cosa hai bisogno?',
      hint: "Indica l'indirizzo dell'officina e se preferisci la consegna o il ritiro al banco.",
      placeholder: 'Es. vorrei conoscere le modalità di consegna per la mia officina.',
      pageTitle: 'Consegne\nnella tua zona.',
      lead: 'Indica dove lavori: il magazzino ti spiega come arrivano i ricambi nella tua zona.'
    },
    'Supporto e formazione': {
      title: 'Parliamo di supporto e formazione', label: 'Quale tema ti interessa?',
      hint: 'Descrivi il tema tecnico o la formazione che stai cercando.',
      placeholder: 'Es. informazioni sulle prossime iniziative formative.',
      pageTitle: 'Supporto\ne formazione.',
      lead: 'Descrivi il tema tecnico o la formazione che ti interessa: il magazzino ti ricontatta.'
    },
    'Rete officine': {
      title: 'Conosciamo la tua officina', label: 'Raccontaci la tua attività',
      hint: 'Ti spieghiamo come funziona la rete e cosa serve per entrarci.',
      placeholder: 'Es. officina multimarca interessata alla rete.',
      pageTitle: 'La rete\ndelle officine.',
      lead: 'Presentaci la tua attività e chiedi un confronto sulla Rete Officine Crocevia.'
    },
    'Altre informazioni': {
      title: 'La tua domanda al magazzino', label: 'Come possiamo aiutarti?',
      hint: 'Inserisci le informazioni utili a capire la tua richiesta.',
      placeholder: 'Scrivi la tua domanda.'
    }
  };

  if (allowedTopics.includes(params.get('tema'))) topic.value = params.get('tema');
  if (allowedCategories.includes(params.get('famiglia'))) category.value = params.get('famiglia');

  function clearError(input) {
    input.removeAttribute('aria-invalid');
    const error = $(`#error-${input.name}`, form);
    if (error) error.hidden = true;
  }

  function applyTopic() {
    const copy = topicCopy[topic.value];
    heading.textContent = copy.title;
    descriptionLabel.replaceChildren(document.createTextNode(copy.label + ' '));
    const requiredMark = document.createElement('span');
    requiredMark.setAttribute('aria-hidden', 'true');
    requiredMark.textContent = '*';
    descriptionLabel.append(requiredMark);
    description.placeholder = copy.placeholder;
    descriptionHelp.textContent = copy.hint;
    const pageHeading = $('[data-contact-title]');
    const pageTitle = copy.pageTitle || 'Parliamo della\ntua richiesta.';
    if (pageHeading.dataset.text !== pageTitle) {
      composeTitle(pageHeading, pageTitle);
      pageHeading.dataset.text = pageTitle;
    }
    $('[data-contact-lead]').textContent = copy.lead || 'Descrivi ciò di cui hai bisogno e scegli come contattare il magazzino.';
    $$('[data-topics]', form).forEach(group => {
      const visible = group.dataset.topics.split('|').includes(topic.value);
      group.hidden = !visible;
      $$('input', group).forEach(input => { input.disabled = !visible; clearError(input); });
    });
    const companyRequired = ['Diventa cliente', 'Rete officine'].includes(topic.value);
    const cityRequired = ['Diventa cliente', 'Consegne e ritiro', 'Rete officine'].includes(topic.value);
    [['azienda', companyRequired], ['comune', cityRequired]].forEach(([name, required]) => {
      const input = $(`#field-${name}`, form);
      const label = $(`label[for="field-${name}"]`, form);
      label.dataset.label ||= label.textContent;
      input.required = required;
      label.replaceChildren(document.createTextNode(label.dataset.label));
      if (required) {
        const mark = document.createElement('span');
        mark.setAttribute('aria-hidden', 'true');
        mark.textContent = ' *';
        label.append(mark);
      }
    });
    categoryContext.hidden = topic.value !== 'Ricambi' || !category.value;
    categoryContext.textContent = category.value ? `Famiglia: ${category.value}` : '';
    errorSummary.hidden = true;
    $$('[aria-invalid]', form).forEach(clearError);
  }

  topic.addEventListener('change', applyTopic);
  form.addEventListener('input', event => {
    if (event.target.matches('input, textarea')) {
      clearError(event.target);
      if (event.target.name === 'tel' || event.target.name === 'email') {
        clearError($('#field-tel', form));
        clearError($('#field-email', form));
      }
      errorSummary.hidden = true;
    }
  });

  /* Scroll a target just below the sticky header. */
  function reveal(element) {
    const offset = ($('.site-header')?.offsetHeight || 0) + 16;
    const top = element.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top: Math.max(0, top), behavior: 'auto' });
  }

  function fail(input, message) {
    input.setAttribute('aria-invalid', 'true');
    const error = $(`#error-${input.name}`, form);
    if (error) { error.textContent = message; error.hidden = false; }
  }

  function currentData() {
    return Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, String(value).trim()]));
  }

  function validate(data) {
    $$('[aria-invalid]', form).forEach(clearError);
    let first = null;
    const add = (name, message) => {
      const input = $(`#field-${name}`, form);
      fail(input, message);
      first ||= input;
    };
    if (!data.desc) add('desc', 'Descrivi brevemente ciò di cui hai bisogno.');
    if (!data.nome) add('nome', 'Inserisci il tuo nome.');
    if (data.tema === 'Diventa cliente' || data.tema === 'Rete officine') {
      if (!data.azienda) add('azienda', "Indica il nome dell'officina o dell'azienda.");
    }
    if (['Diventa cliente', 'Consegne e ritiro', 'Rete officine'].includes(data.tema) && !data.comune) {
      add('comune', "Indica il comune dell'officina.");
    }
    const emailInput = $('#field-email', form);
    if (data.email && !emailInput.validity.valid) add('email', "Controlla l'indirizzo email, per esempio nome@azienda.it.");
    if (!data.tel && !data.email) add('tel', "Inserisci almeno un numero di telefono o un'email.");
    if (data.tel) {
      const digits = data.tel.replace(/\D/g, '');
      if (digits.length < 7 || digits.length > 15 || !/^[+\d\s()./-]+$/.test(data.tel)) {
        add('tel', 'Controlla il numero: inserisci da 7 a 15 cifre, con eventuale prefisso.');
      }
    }
    errorSummary.hidden = !first;
    if (first) {
      const count = $$('[aria-invalid="true"]', form).length;
      errorSummary.textContent = count === 1 ? 'Controlla il campo indicato e riprova.' : `Controlla i ${count} campi indicati e riprova.`;
      first.focus({ preventScroll: true });
      const room = window.innerHeight - ($('.site-header')?.offsetHeight || 0) - 32;
      const span = first.getBoundingClientRect().bottom - errorSummary.getBoundingClientRect().top;
      reveal(span < room ? errorSummary : (first.closest('.field') || first));
      return false;
    }
    return true;
  }

  function buildMessage(data) {
    const pairs = [['Richiesta', data.tema]];
    if (data.tema === 'Ricambi') {
      if (data.famiglia) pairs.push(['Famiglia', data.famiglia]);
      if (data.targa) pairs.push(['Targa o telaio', data.targa.toUpperCase()]);
      if (data.codice) pairs.push(['Codice ricambio', data.codice]);
    }
    pairs.push(['Dettagli', data.desc], ['Nome', data.nome]);
    if (data.azienda) pairs.push(['Officina o azienda', data.azienda]);
    if (data.comune) pairs.push(['Comune', data.comune]);
    if (data.tel) pairs.push(['Telefono', data.tel]);
    if (data.email) pairs.push(['Email', data.email]);
    return pairs;
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = currentData();
    if (!validate(data)) return;
    const pairs = buildMessage(data);
    const list = $('[data-review-list]', form);
    list.replaceChildren();
    pairs.forEach(([label, value]) => {
      const row = document.createElement('div');
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = label;
      dd.textContent = value;
      row.append(dt, dd);
      list.append(row);
    });
    const message = 'Buongiorno Crocevia Ricambi,\n\n' + pairs.map(([label, value]) => `${label}: ${value}`).join('\n\n');
    $('[data-send-wa]', form).href = '#whatsapp-demo';
    $('[data-send-email]', form).href = '#email-demo';
    fields.hidden = true;
    heading.closest('.form-header').hidden = true;
    review.hidden = false;
    review.focus({ preventScroll: true });
    reveal(form.closest('.request-panel') || review);
  });

  $('[data-edit-request]', form).addEventListener('click', () => {
    review.hidden = true;
    fields.hidden = false;
    heading.closest('.form-header').hidden = false;
    topic.focus({ preventScroll: true });
    reveal(form.closest('.request-panel') || topic);
  });

  const contactTitle = $('[data-contact-title]');
  if (contactTitle) contactTitle.dataset.text = topicCopy['Ricambi'].pageTitle;
  applyTopic();
  form.hidden = false;
})();

/* Demo: WhatsApp, email and phone links are simulated. Nothing is opened or sent. */
(() => {
  let toast;
  function show(text) {
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'demo-toast';
      toast.setAttribute('role', 'status');
      document.body.append(toast);
    }
    toast.textContent = text;
    toast.classList.add('is-visible');
    clearTimeout(show.timer);
    show.timer = setTimeout(() => toast.classList.remove('is-visible'), 4200);
  }
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href="#whatsapp-demo"], a[href="#email-demo"], a[href^="mailto:"], a[href^="tel:"]');
    if (!link) return;
    event.preventDefault();
    const href = link.getAttribute('href');
    if (href.startsWith('tel:')) show('Sito dimostrativo: il numero è di fantasia, la chiamata non parte.');
    else if (href === '#whatsapp-demo') show('Sito dimostrativo: WhatsApp non si apre e il messaggio non viene inviato.');
    else show("Sito dimostrativo: l'email non si apre e il messaggio non viene inviato.");
  });
})();
