/* Widget Grist — lecture, recherche, commentaires et veille de la réglementation incendie. */
(function () {
  'use strict';
  const S = window.RegSearch;
  const $ = (sel, el = document) => el.querySelector(sel);
  const esc = S.esc;

  const DOMAINES = {
    ERP: { label: 'Établissements recevant du public', court: 'ERP' },
    IGH: { label: 'Immeubles de grande hauteur', court: 'IGH' },
    HAB: { label: "Bâtiments d'habitation", court: 'Habitation' },
    CDT: { label: 'Code du travail', court: 'Travail' },
    CCH: { label: 'Code de la construction', court: 'CCH' },
  };
  const ORDRE_DOM = ['ERP', 'IGH', 'HAB', 'CDT', 'CCH'];
  const SITESECURITE = { ERP: 'portail-erp.php', IGH: 'portail-igh.php', HAB: 'portail-hab.php', CDT: 'portail-bup.php', CCH: '' };

  // ------------------------------------------------------------------ état
  const st = {
    inGrist: false, nodes: [], byId: new Map(), byRow: new Map(), pos: new Map(), kids: new Map(),
    refLocal: new Map(), refGlobal: new Map(), comments: [], veille: [], syn: null, index: null, idxRows: [],
    domOn: new Set(ORDRE_DOM), mode: 'search', view: null, active: null, pins: [], expanded: new Set(),
    token: null, sideTab: 'cmt', semOn: false,
  };
  const store = {
    get(k, d) { try { const v = localStorage.getItem('regincendie.' + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem('regincendie.' + k, JSON.stringify(v)); } catch (e) { /* stockage indisponible */ } },
  };

  // ------------------------------------------------------------------ utilitaires
  function toast(msg) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove('show'), 2600);
  }
  function fmtDate(d) {
    if (!d) return '';
    const x = new Date(d.length === 10 ? d + 'T12:00:00' : d);
    return isNaN(x) ? d : x.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
  }
  function gDate(v) {
    if (v == null || v === '') return '';
    if (typeof v === 'number') return new Date(v * 1000).toISOString().slice(0, 10);
    return String(v).slice(0, 10);
  }
  function gList(v) { return Array.isArray(v) ? (v[0] === 'L' ? v.slice(1) : v) : (v ? [v] : []); }
  function today() { return new Date().toISOString().slice(0, 10); }
  function dispNum(n) {
    if (!n) return '';
    const num = n.num || '';
    if (/^[LRD]\d{3,4}-/.test(num)) return num.replace(/^([LRD])(\d)/, '$1. $2');
    if (/^\d/.test(num)) return 'Art. ' + num;
    return num.replace(/^([A-Z]+)\s?(\d)/, '$1 $2');
  }
  function plainTitle(n) { return n.type === 'Article' ? dispNum(n) : n.titre; }
  function parseJSON(s, d) { try { return s ? JSON.parse(s) : d; } catch (e) { return d; } }
  function debounce(fn, ms) { let t; const f = (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; f.cancel = () => clearTimeout(t); return f; }

  /* HTML d'un article, filtré par liste blanche (le contenu vient du document) */
  const OK_TAGS = new Set(['P', 'BR', 'TABLE', 'TBODY', 'THEAD', 'TR', 'TD', 'TH', 'UL', 'OL', 'LI', 'B', 'STRONG', 'I', 'EM', 'SUP', 'SUB', 'U', 'DIV', 'SPAN', 'BLOCKQUOTE', 'PRE']);
  function safeHTML(html, fallbackText) {
    if (!html) return (fallbackText || '').split(/\n+/).map((p) => `<p>${esc(p)}</p>`).join('');
    const doc = new DOMParser().parseFromString(`<div>${html}</div>`, 'text/html');
    const walk = (el) => {
      [...el.children].forEach((c) => {
        if (!OK_TAGS.has(c.tagName)) { c.replaceWith(document.createTextNode(c.textContent)); return; }
        [...c.attributes].forEach((a) => { if (!['colspan', 'rowspan'].includes(a.name)) c.removeAttribute(a.name); });
        walk(c);
      });
    };
    const root = doc.body.firstChild; walk(root);
    return root.innerHTML;
  }

  // ------------------------------------------------------------------ chargement des données
  function colsToRows(t) {
    const keys = Object.keys(t); const n = (t.id || []).length; const out = [];
    for (let i = 0; i < n; i++) { const r = {}; for (const k of keys) r[k] = t[k][i]; out.push(r); }
    return out;
  }

  async function fetchAll() {
    const get = async (name) => { try { return await st.ad.fetch(name); } catch (e) { console.warn(name, e); return []; } };
    const [reg, com, vei, syn, par] = await Promise.all([get('REG_Articles'), get('REG_Commentaires'), get('REG_Veille'), get('REG_Synonymes'), get('REG_Parametres')]);
    st.params = Object.fromEntries(par.map((p) => [p.Cle, p.Valeur]));
    return { reg, com, vei, syn };
  }

  function ingest(data) {
    const nodes = data.reg.filter((r) => r.Identifiant).map((r) => ({
      row: r.id, id: r.Identifiant, parent: r.Parent || '', type: r.Type, dom: r.Domaine || 'ERP', num: r.Numero || '',
      titre: r.Titre || '', chemin: r.Chemin || '', niveau: r.Niveau || 0, ordre: r.Ordre || 0, texte: r.Texte || '',
      html: r.Texte_HTML || '', nota: r.Nota || '', etat: r.Etat || '', depuis: gDate(r.En_vigueur_depuis), fin: gDate(r.Fin_de_vigueur),
      hist: parseJSON(r.Historique, []), fut: r.Version_a_venir || '', futHtml: r.Version_a_venir_HTML || '', futDate: gDate(r.Date_a_venir),
      futPar: parseJSON(r.A_venir_par, []), legitext: r.Texte_officiel || '', lien: r.Lien_Legifrance || '',
      tags: gList(r.Mots_cles), vec: r.Vecteur || '', derniere: gDate(r.Derniere_modif_texte),
    })).filter((n) => n.etat !== 'ABROGE');
    nodes.sort((a, b) => a.ordre - b.ordre);
    st.nodes = nodes; st.byId.clear(); st.byRow.clear(); st.pos.clear(); st.kids.clear(); st.refLocal.clear(); st.refGlobal.clear();
    nodes.forEach((n, i) => {
      st.byId.set(n.id, n); st.byRow.set(n.row, n); st.pos.set(n.id, i);
      if (!st.kids.has(n.parent)) st.kids.set(n.parent, []);
      st.kids.get(n.parent).push(n);
      if (n.type === 'Article' && n.num) {
        const k = S.normNum(n.num);
        st.refLocal.set(n.legitext + '|' + k, n);
        if (!st.refGlobal.has(k)) st.refGlobal.set(k, []);
        st.refGlobal.get(k).push(n);
      }
    });
    // nombre d'articles par section
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i]; n.count = n.type === 'Article' ? 1 : (n.count || 0);
      const p = st.byId.get(n.parent); if (p) p.count = (p.count || 0) + n.count;
    }
    ingestComments(data.com);
    st.veille = data.vei.map((v) => ({
      row: v.id, date: gDate(v.Date), dom: v.Domaine || 'Divers', nature: v.Nature || '', titre: v.Titre || '', art: v.Article || 0,
      ancien: v.Ancien_texte || '', nouveau: v.Nouveau_texte || '', source: v.Source || '', lien: v.Lien || '', effet: gDate(v.Date_effet),
      statut: v.Statut || 'À lire', analyse: v.Analyse || '',
    })).sort((a, b) => (b.date || '').localeCompare(a.date || '') || b.row - a.row);
    st.syn = new S.Synonyms(data.syn.filter((s) => s.Terme));
    buildIndex();
  }

  function ingestComments(com) {
    st.comments = com.filter((c) => c.Article).map((c) => ({
      row: c.id, art: c.Article, type: c.Type || '', texte: c.Texte || '', images: gList(c.Images), auteur: c.Auteur || '',
      date: typeof c.Cree_le === 'number' ? new Date(c.Cree_le * 1000).toISOString() : (c.Cree_le || ''),
    })).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    st.cmtBy = new Map();
    for (const c of st.comments) { if (!st.cmtBy.has(c.art)) st.cmtBy.set(c.art, []); st.cmtBy.get(c.art).push(c); }
  }

  function buildIndex() {
    const docs = []; st.idxRows = [];
    for (const n of st.nodes) {
      if (n.type === 'Texte') continue;
      const cm = (st.cmtBy.get(n.row) || []).map((c) => c.texte).join(' ');
      docs.push({
        key: n.id, vec: n.vec,
        fields: { num: n.type === 'Article' ? n.num + ' ' + dispNum(n) : '', path: (n.chemin.split(' › ').slice(-3).join(' ')) + ' ' + n.titre, body: (n.texte || '') + ' ' + (n.fut || ''), extra: n.tags.join(' ') + ' ' + cm },
      });
      st.idxRows.push(n);
    }
    st.index = new S.Index(docs);
    st.idxDocs = docs;
    if (S.Semantic.state === 'ready') S.Semantic.load(docs);
  }

  // ------------------------------------------------------------------ écriture dans Grist
  async function act(actions) {
    try { await st.ad.apply(actions); return true; } catch (e) { console.error(e); toast("Échec de l'enregistrement : " + (e.message || e)); return false; }
  }
  async function token() {
    if (!st.inGrist) return null;
    if (!st.token || st.token.exp < Date.now() + 30000) {
      const t = await grist.docApi.getAccessToken({ readOnly: false });
      st.token = { ...t, exp: Date.now() + (t.ttlMsecs || 300000) };
    }
    return st.token;
  }
  async function attUrl(id) {
    if (!st.inGrist) return id; // en démo, l'« id » est une URL locale
    const t = await token();
    return `${t.baseUrl}/attachments/${id}/download?auth=${t.token}`;
  }
  async function shrink(file) {
    if (!/^image\/(jpeg|png|webp)/.test(file.type)) return file;
    const img = await createImageBitmap(file).catch(() => null);
    if (!img) return file;
    const max = 1800, k = Math.min(1, max / Math.max(img.width, img.height));
    if (k === 1 && file.size < 900000) return file;
    const c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
    const blob = await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.85));
    return new File([blob], file.name.replace(/\.\w+$/, '') + '.jpg', { type: 'image/jpeg' });
  }
  async function upload(files) {
    if (!st.inGrist) return files.map((f) => URL.createObjectURL(f));
    const t = await token(); const fd = new FormData();
    for (const f of files) fd.append('upload', await shrink(f), f.name);
    const r = await fetch(`${t.baseUrl}/attachments?auth=${t.token}`, { method: 'POST', body: fd });
    if (!r.ok) throw new Error('envoi des images refusé (' + r.status + ')');
    return r.json();
  }

  // ------------------------------------------------------------------ références croisées
  const REF_RX = /\b(?:([LRD])\.?\s?(\d{3,4}(?:-\d+){1,2})|(CTS|REF|ITGH|GHTC|GH|CO|GN|GE|AM|AS|CH|CF|DF|EC|EL|GC|GZ|MS|PE|PO|EA|PA|SG|PS|GA|OA|EF|SA|PX|[JLMNOPRSTUVWXY])\s?(\d{1,3})(?:\s?(bis|ter))?|(articles?)\s+(\d{1,3})(?:\s?(bis|ter))?)\b/g;

  function resolveRef(m, ctx) {
    let key;
    if (m[1]) key = m[1] + m[2];
    else if (m[3]) key = m[3] + m[4] + (m[5] ? m[5].toUpperCase() : '');
    else key = m[7] + (m[8] ? m[8].toUpperCase() : '');
    const local = st.refLocal.get(ctx.legitext + '|' + key);
    if (local && local !== ctx) return local;
    if (m[6]) return null; // « article 12 » ne se résout que dans le même texte
    const g = st.refGlobal.get(key);
    if (g && g.length) { const same = g.find((x) => x.dom === ctx.dom); return same || g[0]; }
    return null;
  }

  function linkify(container, ctx) {
    const tw = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
    const todo = [];
    while (tw.nextNode()) todo.push(tw.currentNode);
    for (const tn of todo) {
      const s = tn.nodeValue; REF_RX.lastIndex = 0;
      let m, last = 0, frag = null;
      while ((m = REF_RX.exec(s))) {
        const target = resolveRef(m, ctx);
        if (!target || target === ctx) continue;
        frag = frag || document.createDocumentFragment();
        frag.append(s.slice(last, m.index));
        const b = document.createElement('button');
        b.className = 'ref'; b.type = 'button'; b.textContent = m[0]; b.dataset.ref = target.id;
        b.setAttribute('aria-label', `${m[0]} : aperçu de l'article`);
        frag.append(b); last = m.index + m[0].length;
      }
      if (frag) { frag.append(s.slice(last)); tn.replaceWith(frag); }
    }
  }

  // ------------------------------------------------------------------ popover d'aperçu
  const pop = $('#pop');
  let popT, popHide;
  function showPop(btn) {
    const n = st.byId.get(btn.dataset.ref); if (!n) return;
    pop.className = 'pop show dom-' + n.dom;
    pop.innerHTML = `<header><button class="plate" style="position:static;width:auto;font-size:18px;padding:4px 8px" data-open="${n.id}">${esc(dispNum(n))}</button>
      <span style="display:flex;gap:4px"><button class="btn ghost" data-pin="${n.id}">Épingler</button><button class="btn" data-open="${n.id}">Lire ici</button></span></header>
      <div class="where">${esc(n.chemin.split(' › ').slice(-2).join(' › '))}</div>
      <div class="legal">${safeHTML(n.html, n.texte || n.fut)}</div>`;
    linkify($('.legal', pop), n);
    const r = btn.getBoundingClientRect(); const W = pop.offsetWidth, H = Math.min(pop.offsetHeight, 420);
    let x = Math.min(Math.max(12, r.left), innerWidth - W - 12);
    let y = r.bottom + 8; if (y + H > innerHeight - 10) y = Math.max(10, r.top - H - 8);
    pop.style.left = x + 'px'; pop.style.top = y + 'px';
  }
  function hidePop() { pop.className = 'pop'; }
  document.addEventListener('mouseover', (e) => {
    const b = e.target.closest('.ref');
    if (b) { clearTimeout(popHide); clearTimeout(popT); popT = setTimeout(() => showPop(b), 220); }
    else if (e.target.closest('#pop')) clearTimeout(popHide);
  });
  document.addEventListener('mouseout', (e) => {
    if (e.target.closest('.ref') || e.target.closest('#pop')) { clearTimeout(popT); popHide = setTimeout(hidePop, 350); }
  });
  document.addEventListener('focusin', (e) => { const b = e.target.closest('.ref'); if (b) showPop(b); });

  // ------------------------------------------------------------------ navigation
  function go(view, push = true) {
    st.view = view;
    if (push) { try { history.pushState(view, ''); } catch (e) { /* iframe sans historique */ } }
    hidePop();
    $('#tree').classList.remove('open');
    $('#btnVeille').setAttribute('aria-current', view.v === 'veille' ? 'page' : 'false');
    if (view.v === 'home') renderHome();
    else if (view.v === 'board') renderBoard(view.dom);
    else if (view.v === 'read') renderRead(view.id, view.focus);
    else if (view.v === 'search') renderSearch(view.q);
    else if (view.v === 'ask') renderAsk(view.q);
    else if (view.v === 'veille') renderVeille();
    renderTree();
  }
  window.addEventListener('popstate', (e) => { if (e.state) go(e.state, false); });

  function openNode(id, opts = {}) {
    const n = st.byId.get(id); if (!n) return;
    if (n.type === 'Article') {
      const sec = st.byId.get(n.parent) || n;
      go({ v: 'read', id: sec.id, focus: n.id });
    } else go({ v: 'read', id: n.id, focus: opts.focus });
  }

  function ancestors(n) {
    const out = []; let p = st.byId.get(n.parent);
    while (p) { out.unshift(p); p = st.byId.get(p.parent); }
    return out;
  }
  function descendants(n) {
    const i = st.pos.get(n.id); const out = [];
    for (let j = i + 1; j < st.nodes.length; j++) {
      const x = st.nodes[j];
      if (x.legitext !== n.legitext || (n.type !== 'Texte' && x.niveau <= n.niveau)) break;
      out.push(x);
    }
    return out;
  }

  // ------------------------------------------------------------------ plan par codes
  const ERP_TXT = 'LEGITEXT000020303557';
  const ERP_GROUPES = [
    ['Dispositions communes', [['GN', 'Dispositions communes à tous les ERP']]],
    ['Dispositions générales', [['GE', 'Généralités et contrôle'], ['CO', 'Construction'], ['AM', 'Aménagements, décoration, mobilier'], ['DF', 'Désenfumage'],
      ['CH', 'Chauffage, ventilation, climatisation'], ['GZ', 'Gaz et hydrocarbures liquéfiés'], ['EL', 'Installations électriques'], ['EC', 'Éclairage'],
      ['AS', 'Ascenseurs, escaliers mécaniques'], ['GC', 'Grandes cuisines'], ['MS', 'Moyens de secours']]],
    ["Types d'établissements", [['J', 'Personnes âgées, handicapées'], ['L', 'Salles de réunion, spectacles'], ['M', 'Magasins, centres commerciaux'],
      ['N', 'Restaurants, débits de boissons'], ['O', 'Hôtels, hébergement'], ['P', 'Salles de danse et de jeux'], ['R', 'Enseignement, colonies'],
      ['S', 'Bibliothèques, archives'], ['T', 'Salles d’expositions'], ['U', 'Établissements de soins'], ['V', 'Établissements de culte'],
      ['W', 'Administrations, banques, bureaux'], ['X', 'Établissements sportifs couverts'], ['Y', 'Musées']]],
    ['5e catégorie', [['PE', 'Dispositions générales'], ['PO', 'Hôtels'], ['PU', 'Établissements de soins'], ['PX', 'Établissements sportifs']]],
    ['Établissements spéciaux', [['PA', 'Plein air'], ['CTS', 'Chapiteaux, tentes, structures'], ['SG', 'Structures gonflables'], ['OA', 'Hôtels-restaurants d’altitude'],
      ['REF', 'Refuges de montagne'], ['PS', 'Parcs de stationnement couverts'], ['GA', 'Gares'], ['EF', 'Établissements flottants']]],
  ];
  const prefixOf = (n) => ((n.num || '').match(/^([A-Z]+)\s?\d/) || [])[1] || '';
  const firstInt = (n) => +(((n.num || '').match(/\d+/) || [0])[0]);

  /* Tuiles de navigation d'une réglementation : [{groupe, tuiles:[{code, label, node, arts, de, a, fut, ss}]}] */
  function buildPlans() {
    st.plans = {}; st.tileOf = new Map();
    const lca = (arts) => {
      const chains = arts.map((a) => ancestors(a));
      let out = null;
      for (let i = 0; ; i++) {
        const x = chains[0][i]; if (!x || chains.some((c) => c[i] !== x)) break;
        out = x;
      }
      return out;
    };
    const stat = (arts) => {
      const nums = arts.map(firstInt).filter(Boolean);
      return { arts: arts.length, de: nums.length ? Math.min(...nums) : 0, a: nums.length ? Math.max(...nums) : 0, fut: arts.filter((x) => x.futDate).length };
    };
    // ERP : par codes, comme le règlement et SiteSecurite
    const byCode = new Map();
    for (const n of st.nodes) if (n.type === 'Article' && n.legitext === ERP_TXT) { const p = prefixOf(n); if (p) { if (!byCode.has(p)) byCode.set(p, []); byCode.get(p).push(n); } }
    const erp = ERP_GROUPES.map(([groupe, codes]) => ({
      groupe, tuiles: codes.map(([code, label]) => {
        const arts = byCode.get(code) || [];
        const node = arts.length ? lca(arts) : null;
        const t = { code, label, node: node && node.id, ...stat(arts), ss: ssChapter(code) };
        if (node) st.tileOf.set(node.id, t);
        return t;
      }),
    }));
    const cchErp = st.byId.get('LEGITEXT000006074096#ERP');
    if (cchErp) {
      const t = { code: 'CCH', label: 'Code de la construction (R. 143)', node: cchErp.id, ...stat(descendants(cchErp).filter((x) => x.type === 'Article')), ss: null };
      st.tileOf.set(cchErp.id, t);
      erp.push({ groupe: 'Code de la construction', tuiles: [t] });
    }
    st.plans.ERP = erp;
    // autres réglementations : chapitres du texte, en sautant les niveaux à un seul enfant
    const secsOf = (x) => (st.kids.get(x.id) || []).filter((k) => k.type === 'Section');
    const deep = (x) => { for (;;) { const k = st.kids.get(x.id) || []; const sc = k.filter((y) => y.type === 'Section'); if (sc.length === 1 && !k.some((y) => y.type === 'Article')) x = sc[0]; else return x; } };
    const tile = (sec, txt) => {
      const arts = (sec === txt ? descendants(txt) : [sec, ...descendants(sec)]).filter((x) => x.type === 'Article');
      const p = arts.length ? prefixOf(arts[0]) : '';
      const codeArt = arts.length && (arts[0].num || '').match(/^([LR])(\d{3,4})-/);
      const cls = sec.titre.match(/:\s*(GH ?[A-Z]{1,2}|GHTC|ITGH)\s*:\s*(.*)$/);
      const m = sec.titre.match(/^(titre|chapitre|section|sous-section|livre)\s+([ivxlcdm]+|\d+)(?:er)?\b\s*:?\s*(.*)$/i);
      let code = m ? m[2].toUpperCase() : (p || '§');
      let label = (m ? m[3] : sec.titre).replace(/\.$/, '') || sec.titre;
      if (cls) { code = cls[1].replace(/\s/g, ' '); label = cls[2]; }
      else if (codeArt) code = `${codeArt[1]}. ${codeArt[2]}`;
      const t = { code, label, node: sec.id, ...stat(arts), prefix: codeArt ? '' : p, ss: p ? ssChapter(p) : null };
      if (codeArt) t.range = arts.length > 1 ? `${dispNum(arts[0])} à ${dispNum(arts[arts.length - 1])}` : dispNum(arts[0]);
      st.tileOf.set(sec.id, t);
      return t;
    };
    /* dans un groupe, des tuiles au même code (« R. 4216 ») prennent leur premier numéro d'article */
    const distinct = (tuiles) => {
      const n = new Map(); tuiles.forEach((t) => n.set(t.code, (n.get(t.code) || 0) + 1));
      tuiles.forEach((t) => { if (n.get(t.code) > 1 && t.range) { const a = st.byId.get(t.node); const first = [a, ...descendants(a)].find((x) => x.type === 'Article'); if (first) t.code = first.num.replace(/^[LR]/, ''); } });
      return tuiles;
    };
    for (const dom of ORDRE_DOM) {
      if (dom === 'ERP') continue;
      const groupes = [];
      for (const txt of st.nodes.filter((n) => n.type === 'Texte' && n.dom === dom)) {
        let top = txt;
        while (secsOf(top).length === 1) top = secsOf(top)[0];
        const court = txt.titre.replace(/ portant .*| relatif .*| pris pour .*/i, '').replace(/^Code de la construction et de l'habitation — .*/, 'Code de la construction et de l\'habitation');
        const secs = secsOf(top);
        if (!secs.length) { groupes.push({ groupe: court, tuiles: [tile(txt, txt)] }); continue; }
        if (secs.length >= 5) { groupes.push({ groupe: court, tuiles: secs.map((x) => tile(deep(x), txt)) }); continue; }
        const seuls = [];
        for (const sec0 of secs) {
          const sec = deep(sec0);
          const sub = secsOf(sec).map(deep);
          if (sub.length > 1) groupes.push({ groupe: secs.length > 1 && /^partie/i.test(sec0.titre) ? `${court} — ${sec0.titre.toLowerCase()}` : sec.titre, tuiles: sub.map((x) => tile(x, txt)) });
          else seuls.push(tile(sec, txt));
        }
        if (seuls.length) groupes.push({ groupe: court, tuiles: seuls });
      }
      groupes.forEach((g) => distinct(g.tuiles));
      st.plans[dom] = groupes;
    }
  }

  /* Liens SiteSecurite (plan des pages, sans contenu) */
  function ssChapter(code) { const c = st.ss && st.ss.chapitres && st.ss.chapitres[code]; return c ? c.url : null; }
  function ssPortal(dom) { return (st.ss && st.ss.portails && st.ss.portails[dom]) || 'https://sitesecurite.com/' + (SITESECURITE[dom] || ''); }
  function ssLink(n) {
    const p = prefixOf(n), k = firstInt(n);
    const pages = st.ss && st.ss.erp && st.ss.erp[p];
    if (pages) { const r = pages.find((x) => x.de <= k && k <= x.a); if (r) return { url: r.url, label: r.libelle }; }
    if (ssChapter(p)) return { url: ssChapter(p), label: p };
    return { url: ssPortal(n.dom), label: null };
  }
  /* Tuile (chapitre/code) qui contient un nœud */
  function tileFor(n) {
    if (!n) return null;
    if (st.tileOf.has(n.id)) return st.tileOf.get(n.id);
    for (const a of ancestors(n).reverse()) if (st.tileOf.has(a.id)) return st.tileOf.get(a.id);
    return null;
  }
  const rangeTxt = (t) => t.range || (t.de ? `${t.prefix || (/^[A-Z]+$/.test(t.code) && t.code !== 'CCH' ? t.code : 'Art.')} ${t.de}${t.a !== t.de ? ' à ' + t.a : ''}` : '');

  // ------------------------------------------------------------------ tableau des codes
  function renderBoard(dom) {
    setSide(false);
    const plan = st.plans[dom] || [];
    $('#read').className = 'pane readpane dom-' + dom;
    $('#read').innerHTML = `<div class="board">
      <div class="boardhead"><h1>${esc(DOMAINES[dom].label)}</h1>
      <a class="sslink" href="${esc(ssPortal(dom))}" target="_blank" rel="noopener">Portail ${esc(DOMAINES[dom].court)} sur SiteSecurite ↗</a></div>
      <p class="hint">Cliquez un ${dom === 'ERP' ? 'code' : 'chapitre'} pour lire tous ses articles à la suite. Raccourci : tapez ${dom === 'ERP' ? '« CO », « L » ou « CO 15 »' : 'un numéro d’article'} dans la recherche puis Entrée.</p>
      ${plan.map((g) => `<section class="bgroup"><h2>${esc(g.groupe)}</h2><div class="tiles">${g.tuiles.map((t) => tileHTML(t, dom)).join('')}</div></section>`).join('')}
    </div>`;
    $('#read').scrollTop = 0;
  }
  function tileHTML(t, dom) {
    const open = t.node ? `data-open="${t.node}"` : (t.ss ? `data-href="${esc(t.ss)}"` : 'disabled');
    return `<button class="tile dom-${dom}" ${open} title="${esc(t.label)}">
      <span class="tcode${t.code.length > 3 ? ' long' : ''}">${esc(t.code)}</span>
      <span class="tlabel">${esc(t.label)}</span>
      <span class="tmeta">${t.node ? `${esc(rangeTxt(t))}${t.fut ? ` · <b class="tfut">${t.fut} à venir</b>` : ''}` : 'Sur SiteSecurite ↗'}</span></button>`;
  }

  /* Barre des codes, toujours visible pendant la lecture */
  function railHTML(dom, current) {
    const plan = st.plans[dom] || []; if (!plan.length) return '';
    return `<nav class="rail" aria-label="Accès rapide aux chapitres"><button class="rhome" data-board="${dom}" title="Tous les ${dom === 'ERP' ? 'codes' : 'chapitres'}">▦</button>${plan.map((g) =>
      `<span class="rg" title="${esc(g.groupe)}"></span>` + g.tuiles.filter((t) => t.node).map((t) => `<button class="rp${current && current.node === t.node ? ' on' : ''}" data-open="${t.node}" title="${esc(t.code + ' — ' + t.label)}">${esc(t.code)}</button>`).join('')).join('')}</nav>`;
  }

  /* En-tête de chapitre : sommaire en tuiles + grille des numéros + accès SiteSecurite */
  function chapHeadHTML(n, t) {
    const secs = (st.kids.get(n.id) || []).filter((x) => x.type === 'Section');
    const arts = [n, ...descendants(n)].filter((x) => x.type === 'Article');
    const pref = t.prefix || (/^[A-Z]+$/.test(t.code) ? t.code : '');
    const ssPages = pref && st.ss && st.ss.erp ? st.ss.erp[pref] || [] : [];
    const toc = secs.map((sec) => {
      const a = [sec, ...descendants(sec)].filter((x) => x.type === 'Article');
      const nums = a.map(firstInt).filter(Boolean);
      const lo = Math.min(...nums), hi = Math.max(...nums);
      const pages = ssPages.filter((p) => p.de <= hi && p.a >= lo);
      return `<div class="tocitem"><button data-gosec="${sec.id}"><span class="trange">${a.length ? esc((pref ? pref + ' ' : '') + lo + (hi !== lo ? '–' + hi : '')) : ''}</span>${esc(sec.titre.replace(/^(section|sous-section|chapitre)\s+[^:]*:\s*/i, ''))}</button>${pages.length === 1 ? `<a href="${esc(pages[0].url)}" target="_blank" rel="noopener" class="ssmini" title="Ouvrir ${esc(pages[0].libelle)} sur SiteSecurite">SS ↗</a>` : ''}</div>`;
    }).join('');
    return `<header class="chap">
      <div class="chaptop"><span class="bigplate">${esc(t.code)}</span>
        <div class="chaptitle"><h1>${esc(t.label)}</h1>
          <p class="hint">${esc(n.titre)} · ${arts.length} article${arts.length > 1 ? 's' : ''}${t.fut ? ` · <b class="tfut">${t.fut} modifié${t.fut > 1 ? 's' : ''} prochainement</b>` : ''}</p>
          <div class="chapacts">
            ${t.ss ? `<a class="btn ghost" href="${esc(t.ss)}" target="_blank" rel="noopener">Ouvrir ${esc(t.code)} sur SiteSecurite ↗</a>` : ''}
            ${n.lien ? `<a class="btn ghost" href="${esc(n.lien)}" target="_blank" rel="noopener">Légifrance ↗</a>` : ''}
            <label class="goto">Aller à ${pref ? esc(pref) : 'l’article'} <input id="gotoNum" inputmode="numeric" placeholder="n°" aria-label="Numéro d'article"></label>
          </div></div></div>
      ${toc ? `<div class="toc">${toc}</div>` : ''}
      <div class="numgrid big">${arts.map((a) => `<button data-goart="${a.id}" class="${a.futDate ? 'chg' : ''}" title="${esc(dispNum(a))}${a.futDate ? ' — modifié le ' + fmtDate(a.futDate) : ''}">${esc(dispNum(a).replace(/^Art\. /, ''))}</button>`).join('')}</div>
    </header>`;
  }

  function scrollToItem(id, isSection) {
    if (!readCtx) return;
    const i = readCtx.items.findIndex((x) => x.id === id);
    if (i < 0) { openNode(id); return; }
    if (i >= readCtx.shown) renderMore(i + 25);
    const el = document.getElementById((isSection ? 's-' : 'a-') + id);
    if (!el) return;
    st.pinActive = Date.now() + 1200;
    el.scrollIntoView({ block: 'start' });
    if (!isSection) { el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash'); setActive(st.byId.get(id)); }
    else { const first = readCtx.items.slice(i).find((x) => x.type === 'Article'); if (first) setActive(first); }
  }

  // ------------------------------------------------------------------ arbre
  const chev = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="m9 6 6 6-6 6"/></svg>';
  function renderTree() {
    const sel = st.view && st.view.v === 'read' ? st.byId.get(st.view.id) : null;
    if (sel) { ancestors(sel).forEach((a) => st.expanded.add(a.id)); }
    const texts = st.nodes.filter((n) => n.type === 'Texte');
    let h = '';
    for (const d of ORDRE_DOM) {
      if (!st.domOn.has(d)) continue;
      const tx = texts.filter((t) => t.dom === d); if (!tx.length) continue;
      const cur = tileFor(sel);
      h += `<div class="dom-${d}"><button class="tdom" data-board="${d}"><span class="bar"></span>${esc(DOMAINES[d].label)}</button>`;
      for (const g of st.plans[d] || []) {
        h += `<div class="tgroup">${esc(g.groupe)}</div><ul class="codelist">`;
        for (const t of g.tuiles) {
          h += `<li><button class="ci${cur && cur.node === t.node && t.node ? ' sel' : ''}" ${t.node ? `data-open="${t.node}"` : (t.ss ? `data-href="${esc(t.ss)}"` : 'disabled')}><span class="cc${t.code.length > 4 ? ' long' : ''}">${esc(t.code)}</span><span class="cl">${esc(t.label)}</span><span class="cnt">${t.node ? t.arts : '↗'}</span></button></li>`;
        }
        h += '</ul>';
      }
      h += `<details class="plan"${sel && sel.dom === d && !cur ? ' open' : ''}><summary>Plan officiel des textes</summary><ul class="tree" role="tree">`;
      for (const t of tx) h += treeItem(t, sel);
      h += '</ul></details></div>';
    }
    $('#tree').innerHTML = h || '<p class="empty">Aucune réglementation sélectionnée.</p>';
    const s = $('#tree .ci.sel') || $('#tree .tn.sel') || (st.view && st.view.v === 'board' && $(`#tree [data-board="${st.view.dom}"]`));
    if (s) s.scrollIntoView({ block: st.view && st.view.v === 'board' ? 'start' : 'nearest' });
  }
  function treeItem(n, sel) {
    const kids = (st.kids.get(n.id) || []);
    const secs = kids.filter((k) => k.type !== 'Article');
    const arts = kids.filter((k) => k.type === 'Article');
    const open = st.expanded.has(n.id);
    const lbl = n.type === 'Texte' ? n.titre.replace(/ portant .*| relatif .*| pris pour .*/i, '') : n.titre;
    let h = `<li><div class="tn${sel && sel.id === n.id ? ' sel' : ''}" aria-expanded="${open}">
      ${secs.length || arts.length ? `<button class="tw" data-tog="${n.id}" aria-label="${open ? 'Replier' : 'Déplier'}">${chev}</button>` : '<span style="width:20px;flex:none"></span>'}
      <button class="tl" data-open="${n.id}" title="${esc(n.titre)}">${esc(lbl)}<span class="cnt">${n.count || 0}</span></button></div>`;
    if (open) {
      if (arts.length) h += `<div class="numgrid">${arts.map((a) => `<button data-open="${a.id}" class="${a.futDate ? 'chg' : ''}" title="${esc(dispNum(a))}${a.futDate ? ' — modifié le ' + fmtDate(a.futDate) : ''}">${esc(dispNum(a).replace('Art. ', ''))}</button>`).join('')}</div>`;
      if (secs.length) h += `<ul class="tree" role="group">${secs.map((k) => treeItem(k, sel)).join('')}</ul>`;
    }
    return h + '</li>';
  }

  // ------------------------------------------------------------------ accueil
  function renderHome() {
    setSide(false);
    const arts = st.nodes.filter((n) => n.type === 'Article' && st.domOn.has(n.dom));
    const fut = arts.filter((n) => n.futDate).sort((a, b) => a.futDate.localeCompare(b.futDate));
    const rec = arts.filter((n) => n.depuis).sort((a, b) => b.depuis.localeCompare(a.depuis)).slice(0, 10);
    const lastCm = st.comments.slice(0, 8);
    const signs = ORDRE_DOM.filter((d) => st.domOn.has(d)).map((d) => {
      const a = arts.filter((n) => n.dom === d); if (!a.length) return '';
      const last = a.reduce((m, n) => (n.depuis > m ? n.depuis : m), '');
      const nf = a.filter((n) => n.futDate).length;
      const txt = st.nodes.find((n) => n.type === 'Texte' && n.dom === d);
      return `<button class="sign dom-${d}" data-board="${d}"><b>${esc(DOMAINES[d].court)}</b>
        <span>${esc(DOMAINES[d].label)}</span>
        <small>${a.length.toLocaleString('fr-FR')} articles · dernière modification ${fmtDate(last)}${nf ? ` · ${nf} à venir` : ''}</small></button>`;
    }).join('');
    const li = (n, sub) => `<li class="dom-${n.dom}"><button data-open="${n.id}"><span class="mini">${esc(dispNum(n).replace('Art. ', ''))}</span><span>${esc(n.chemin.split(' › ').slice(-1)[0] || '')}<span class="sub">${sub}</span></span></button></li>`;
    $('#read').innerHTML = `<div class="home">
      <h1>Réglementation sécurité incendie</h1>
      <p class="lead">Textes officiels consolidés (Légifrance)${st.params && st.params.base_legifrance ? `, à jour au ${fmtDate(st.params.base_legifrance)}` : ''}. Survolez une référence citée pour lire l'article sans quitter la page ; commentez et illustrez chaque article.</p>
      <div class="signs">${signs}</div>
      <div class="cols">
        <section><h2>Changements à venir</h2>${fut.length ? `<ul class="list">${fut.slice(0, 12).map((n) => li(n, 'Nouvelle rédaction au ' + fmtDate(n.futDate))).join('')}</ul>` : '<p class="hint">Aucune modification programmée.</p>'}</section>
        <section><h2>Modifiés récemment</h2><ul class="list">${rec.map((n) => li(n, 'En vigueur depuis le ' + fmtDate(n.depuis))).join('')}</ul></section>
        <section><h2>Derniers commentaires</h2>${lastCm.length ? `<ul class="list">${lastCm.map((c) => { const n = st.byRow.get(c.art); return n ? li(n, esc(c.auteur || '') + ' : ' + esc(c.texte.slice(0, 90))) : ''; }).join('')}</ul>` : '<p class="hint">Aucun commentaire pour l’instant. Ouvrez un article et ajoutez le premier.</p>'}</section>
      </div></div>`;
    $('#read').scrollTop = 0;
  }

  // ------------------------------------------------------------------ lecture continue
  let readCtx = null;
  const stickObs = new ResizeObserver((es) => { for (const e of es) document.documentElement.style.setProperty('--stick-h', Math.round(e.target.getBoundingClientRect().height) + 'px'); });
  function renderRead(id, focus) {
    const n = st.byId.get(id); if (!n) return renderHome();
    const items = descendants(n);
    const anc = ancestors(n);
    const crumbs = [...anc, n].map((a, i, arr) => `<button data-open="${a.id}">${esc(a.type === 'Texte' ? DOMAINES[a.dom].label : a.titre)}</button>${i < arr.length - 1 ? '<span class="sep">›</span>' : ''}`).join('');
    const own = n.type === 'Article' ? [n] : [];
    readCtx = { root: n, items: own.concat(items), shown: 0 };
    const tile = tileFor(n);
    const isChap = tile && tile.node === n.id;
    $('#read').className = 'pane readpane dom-' + n.dom;
    $('#read').innerHTML = `<div class="stick">${railHTML(n.dom, tile)}<div class="crumbs">${crumbs}</div></div><div class="reading">
      ${isChap ? chapHeadHTML(n, tile) : `<div class="sechead l1"><h2>${esc(n.titre)}</h2>
      <p class="hint" style="margin:6px 0 0">${n.count || 0} article${n.count > 1 ? 's' : ''}${n.lien ? ` · <a href="${esc(n.lien)}" target="_blank" rel="noopener">version officielle sur Légifrance</a>` : ''}</p></div>`}
      <div id="flow"></div></div>`;
    stickObs.disconnect(); stickObs.observe($('.stick'));
    const rp = $('.rail .rp.on'); if (rp) rp.scrollIntoView({ block: 'nearest', inline: 'center' });
    const gi = $('#gotoNum');
    if (gi) gi.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter') return;
      const v = gi.value.trim().toUpperCase(); if (!v) return;
      const pref = tile.prefix || (/^[A-Z]+$/.test(tile.code) ? tile.code : '');
      const want = S.normNum((/^\d/.test(v) && pref ? pref : '') + v);
      const hit = readCtx.items.find((x) => x.type === 'Article' && S.normNum(x.num) === want);
      if (hit) { gi.value = ''; scrollToItem(hit.id); } else toast(`Pas d'article ${(/^\d/.test(v) && pref ? pref + ' ' : '') + v} dans ce chapitre`);
    });
    let target = focus ? readCtx.items.findIndex((x) => x.id === focus) : -1;
    renderMore(Math.max(60, target + 25));
    if (target >= 0) {
      const el = document.getElementById('a-' + focus);
      if (el) { el.scrollIntoView({ block: 'start' }); el.classList.add('flash'); setActive(st.byId.get(focus)); }
    } else {
      $('#read').scrollTop = 0;
      const first = readCtx.items.find((x) => x.type === 'Article'); if (first) setActive(first);
    }
    observeArticles();
  }
  function renderMore(upTo) {
    const flow = $('#flow'); if (!flow || !readCtx) return;
    const end = Math.min(readCtx.items.length, Math.max(upTo || 0, readCtx.shown + 60));
    let h = '';
    for (let i = readCtx.shown; i < end; i++) h += itemHTML(readCtx.items[i]);
    $('.more', flow) && $('.more', flow).remove();
    flow.insertAdjacentHTML('beforeend', h);
    for (let i = readCtx.shown; i < end; i++) {
      const it = readCtx.items[i];
      if (it.type === 'Article') { const el = document.getElementById('a-' + it.id); if (el) linkify($('.legal', el), it); }
    }
    readCtx.shown = end;
    if (end < readCtx.items.length) {
      flow.insertAdjacentHTML('beforeend', `<button class="more" id="more">Afficher la suite (${readCtx.items.length - end} éléments)</button>`);
      moreObs.observe($('#more'));
    }
    observeArticles();
  }
  const moreObs = new IntersectionObserver((es) => { es.forEach((e) => { if (e.isIntersecting) { moreObs.unobserve(e.target); renderMore(); } }); }, { root: null, rootMargin: '600px' });

  function itemHTML(it) {
    if (it.type !== 'Article') {
      const rel = it.niveau - readCtx.root.niveau;
      return `<div class="sechead${rel <= 1 ? ' l1' : ''}" id="s-${it.id}">${rel <= 1 ? `<h2>${esc(it.titre)}</h2>` : `<h3>${esc(it.titre)}</h3>`}</div>`;
    }
    const nc = (st.cmtBy.get(it.row) || []).length;
    const imgs = (st.cmtBy.get(it.row) || []).flatMap((c) => c.images).slice(0, 6);
    const recent = it.depuis && it.depuis >= new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10);
    return `<article class="art dom-${it.dom}${it.etat === 'A_VENIR' ? ' abroge' : ''}" id="a-${it.id}" data-art="${it.id}">
      <button class="plate" data-focus="${it.id}" aria-label="Commentaires et historique de ${esc(dispNum(it))}">${esc(dispNum(it))}${it.etat === 'A_VENIR' ? '<small>à venir</small>' : ''}</button>
      <div class="artbody">
        ${it.etat === 'A_VENIR' ? `<p class="pill warn">Entre en vigueur le ${fmtDate(it.futDate)}</p>` : `<div class="legal">${safeHTML(it.html, it.texte)}</div>`}
        ${it.nota ? `<div class="nota"><b>Nota :</b> ${esc(it.nota)}</div>` : ''}
        ${it.fut ? `<details class="future"${it.etat === 'A_VENIR' ? ' open' : ''}><summary><b>Nouvelle rédaction au ${fmtDate(it.futDate)}</b> — voir les changements</summary><div class="legal diff" data-diff="${it.id}"></div></details>` : ''}
        <div class="meta">
          ${it.depuis ? `<span class="pill${recent ? ' new' : ''}">En vigueur depuis le ${fmtDate(it.depuis)}</span>` : ''}
          ${it.futDate && it.etat !== 'A_VENIR' ? `<span class="pill warn">Modifié au ${fmtDate(it.futDate)}</span>` : ''}
          ${it.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}
        </div>
        ${imgs.length ? `<div class="thumbs" data-imgs="${it.row}"></div>` : ''}
        <div class="acts">
          <button data-focus="${it.id}" data-tab="cmt">💬 ${nc ? nc + ' commentaire' + (nc > 1 ? 's' : '') : 'Commenter'}</button>
          <button data-pin="${it.id}">📌 Épingler</button>
          <button data-copy="${it.id}">Copier la référence</button>
          ${it.lien ? `<a href="${esc(it.lien)}" target="_blank" rel="noopener">Légifrance ↗</a>` : ''}
          ${(() => { const l = ssLink(it); return l.label ? `<a class="ss" href="${esc(l.url)}" target="_blank" rel="noopener" title="Ouvrir la page SiteSecurite qui contient cet article">SiteSecurite · ${esc(l.label)} ↗</a>` : `<button data-ss="${it.id}">SiteSecurite ↗</button>`; })()}
        </div>
      </div></article>`;
  }

  // vignettes et diffs à la demande
  document.addEventListener('toggle', (e) => {
    const d = e.target; if (!(d instanceof HTMLDetailsElement) || !d.open) return;
    const box = $('[data-diff]', d); if (!box || box.dataset.done) return;
    const n = st.byId.get(box.dataset.diff);
    box.innerHTML = n.texte ? diffHTML(n.texte, n.fut) : safeHTML(n.futHtml, n.fut);
    box.dataset.done = 1;
  }, true);

  const artObs = new IntersectionObserver((es) => {
    for (const e of es) {
      if (e.isIntersecting) {
        const t = e.target.querySelector('[data-imgs]');
        if (t && !t.dataset.done) { t.dataset.done = 1; fillThumbs(t, +t.dataset.imgs); }
      }
    }
    pickActive();
  }, { root: null, threshold: [0, 0.2] });
  function observeArticles() { document.querySelectorAll('.art:not([data-obs])').forEach((a) => { a.dataset.obs = 1; artObs.observe(a); }); }
  const pickActive = debounce(() => {
    if (st.view.v !== 'read' || st.pinActive > Date.now()) return;
    const top = $('#read').getBoundingClientRect().top + 70;
    let best = null;
    for (const a of document.querySelectorAll('.art')) {
      const r = a.getBoundingClientRect();
      if (r.bottom > top + 20) { best = a; break; }
    }
    if (best) setActive(st.byId.get(best.dataset.art));
  }, 180);
  $('#read').addEventListener('scroll', pickActive, { passive: true });

  async function fillThumbs(el, row) {
    const ids = (st.cmtBy.get(row) || []).flatMap((c) => c.images).slice(0, 6);
    const urls = await Promise.all(ids.map(attUrl));
    el.innerHTML = urls.map((u) => `<img src="${esc(u)}" alt="Illustration jointe à un commentaire" loading="lazy" data-zoom>`).join('');
  }

  // ------------------------------------------------------------------ panneau latéral
  function setSide(show) {
    $('#main').classList.toggle('noside', !show);
    if (!show) $('#side').innerHTML = '';
  }
  function setActive(n, tab) {
    if (!n) return;
    if (tab) st.sideTab = tab;
    if (st.active === n && !tab) return;
    st.active = n;
    document.querySelectorAll('.art.active').forEach((a) => a.classList.remove('active'));
    const el = document.getElementById('a-' + n.id); if (el) el.classList.add('active');
    setSide(true); renderSide();
  }
  function renderSide() {
    const n = st.active; if (!n) return;
    const cm = st.cmtBy.get(n.row) || [];
    const tabs = [['cmt', `Commentaires${cm.length ? ' (' + cm.length + ')' : ''}`], ['hist', 'Historique'], ['pins', `Épinglés${st.pins.length ? ' (' + st.pins.length + ')' : ''}`]];
    let body = '';
    if (st.sideTab === 'cmt') {
      body = `<div class="tags" aria-label="Mots-clés">${n.tags.map((t) => `<span class="tag">${esc(t)}<button data-untag="${esc(t)}" aria-label="Retirer ${esc(t)}">×</button></span>`).join('')}
        <input id="tagIn" type="text" placeholder="+ mot-clé" style="border:0;background:none;padding:2px 4px;width:110px;font-size:13px" aria-label="Ajouter un mot-clé"></div>
        ${cm.length ? cm.map((c) => `<div class="cmt"><div class="who">${c.type ? `<span class="pill">${esc(c.type)}</span>` : ''}<b>${esc(c.auteur || 'Anonyme')}</b><span>${fmtDate(c.date)}</span></div>
          ${c.texte ? `<div class="txt">${esc(c.texte)}</div>` : ''}${c.images.length ? `<div class="thumbs" data-cimgs="${c.row}"></div>` : ''}</div>`).join('') : '<p class="hint" style="margin-top:10px">Pas encore de commentaire sur cet article.</p>'}
        <form class="form" id="cform">
          <select name="type" aria-label="Type de commentaire">${['Interprétation', 'Retour terrain', 'Photo / schéma', 'Question', 'Jurisprudence', 'Doctrine / réponse ministérielle'].map((t) => `<option>${t}</option>`).join('')}</select>
          <textarea name="texte" placeholder="Votre interprétation, un retour de visite, une question…" aria-label="Commentaire"></textarea>
          <label class="drop" id="drop">Glissez des photos ou schémas ici, ou <u>choisissez des fichiers</u><input type="file" name="files" accept="image/*" multiple hidden></label>
          <div class="thumbs" id="preview"></div>
          <button class="btn" type="submit">Publier le commentaire</button>
        </form>`;
    } else if (st.sideTab === 'hist') {
      const hist = n.hist || [];
      body = `<ul class="hist">
        ${n.depuis ? `<li><b>Version en vigueur depuis le ${fmtDate(n.depuis)}</b></li>` : ''}
        ${hist.slice().reverse().map((h) => `<li>${esc({ MODIFIE: 'Modifié par', CREE: 'Créé par', CREATION: 'Créé par', TRANSFERE: 'Transféré par', ABROGE: 'Abrogé par' }[h.type] || h.type)} ${esc(h.texte)}</li>`).join('') || '<li class="hint">Aucune modification depuis la version initiale.</li>'}
        </ul>
        ${n.fut ? `<h3 style="font-size:14px;margin:16px 0 6px">Nouvelle rédaction au ${fmtDate(n.futDate)}</h3><p class="hint">${esc((n.futPar || []).map((h) => h.texte).join(' ; '))}</p><div class="legal diff" style="font-size:13.5px">${n.texte ? diffHTML(n.texte, n.fut) : esc(n.fut)}</div>` : ''}
        <p style="margin-top:14px">${n.lien ? `<a href="${esc(n.lien)}" target="_blank" rel="noopener">Historique complet sur Légifrance ↗</a>` : ''}</p>`;
    } else {
      body = st.pins.length ? st.pins.map((id) => { const p = st.byId.get(id); return p ? `<div class="pin dom-${p.dom}"><header><button class="plate" style="position:static;width:auto;font-size:16px;padding:3px 7px" data-open="${p.id}">${esc(dispNum(p))}</button><button class="iconbtn" data-unpin="${p.id}" aria-label="Retirer">×</button></header><div class="legal" data-pinbody="${p.id}">${safeHTML(p.html, p.texte || p.fut)}</div></div>` : ''; }).join('')
        : '<p class="hint">Épinglez des articles pour les garder sous les yeux pendant la lecture, par exemple pour comparer deux dispositions.</p>';
    }
    $('#side').innerHTML = `<div class="side-h dom-${n.dom}"><button class="plate" data-open="${n.id}">${esc(dispNum(n))}</button>
      <div class="t">${esc(n.chemin.split(' › ').slice(-2).join(' › '))}</div>
      <div class="tabs" role="tablist">${tabs.map(([k, l]) => `<button role="tab" aria-selected="${st.sideTab === k}" data-stab="${k}">${l}</button>`).join('')}</div></div>
      <div class="side-b">${body}</div>`;
    document.querySelectorAll('#side [data-cimgs]').forEach(async (el) => {
      const c = st.comments.find((x) => x.row === +el.dataset.cimgs);
      const urls = await Promise.all(c.images.map(attUrl));
      el.innerHTML = urls.map((u) => `<img src="${esc(u)}" alt="Image jointe" data-zoom>`).join('');
    });
    document.querySelectorAll('#side [data-pinbody]').forEach((el) => linkify(el, st.byId.get(el.dataset.pinbody)));
    wireForm(n);
  }

  function wireForm(n) {
    const f = $('#cform'); if (!f) return;
    let files = [];
    const drop = $('#drop', f), input = f.files;
    const show = () => { $('#preview', f).innerHTML = files.map((x) => `<img src="${URL.createObjectURL(x)}" alt="">`).join(''); };
    input.addEventListener('change', () => { files = files.concat([...input.files]); show(); });
    ['dragover', 'dragenter'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
    ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove('over')));
    drop.addEventListener('drop', (e) => { e.preventDefault(); files = files.concat([...e.dataTransfer.files].filter((x) => x.type.startsWith('image/'))); show(); });
    f.texte.addEventListener('paste', (e) => {
      const imgs = [...(e.clipboardData || {}).files || []].filter((x) => x.type.startsWith('image/'));
      if (imgs.length) { files = files.concat(imgs); show(); }
    });
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const texte = f.texte.value.trim();
      if (!texte && !files.length) { toast('Écrivez un commentaire ou ajoutez une image.'); return; }
      const btn = $('button[type=submit]', f); btn.disabled = true; btn.textContent = 'Publication…';
      try {
        const ids = files.length ? await upload(files) : [];
        const rec = { Article: n.row, Type: f.type.value, Texte: texte };
        if (ids.length) rec.Images = ['L', ...ids];
        const ok = await act([['AddRecord', 'REG_Commentaires', null, rec]]);
        if (ok) { toast('Commentaire publié'); await reload(); }
      } catch (err) { toast('Échec : ' + err.message); btn.disabled = false; btn.textContent = 'Publier le commentaire'; }
    });
    const tagIn = $('#tagIn');
    tagIn.addEventListener('keydown', async (e) => {
      if (e.key !== 'Enter' || !tagIn.value.trim()) return;
      e.preventDefault();
      const tags = [...new Set([...n.tags, tagIn.value.trim()])];
      if (await act([['UpdateRecord', 'REG_Articles', n.row, { Mots_cles: ['L', ...tags] }]])) { n.tags = tags; renderSide(); refreshArticle(n); buildIndex(); }
    });
  }
  function refreshArticle(n) {
    const el = document.getElementById('a-' + n.id); if (!el || !readCtx) return;
    el.outerHTML = itemHTML(n);
    const nel = document.getElementById('a-' + n.id); linkify($('.legal', nel), n); nel.classList.add('active'); observeArticles();
  }

  // ------------------------------------------------------------------ diff mot à mot
  function diffHTML(a, b) {
    const A = a.split(/(\s+)/), B = b.split(/(\s+)/);
    const n = A.length, m = B.length;
    if (n * m > 6e6) return `<p><b>Texte actuel</b></p><p>${esc(a)}</p><p><b>Nouvelle rédaction</b></p><p>${esc(b)}</p>`;
    const dp = new Uint32Array((n + 1) * (m + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i * (m + 1) + j] = A[i] === B[j] ? dp[(i + 1) * (m + 1) + j + 1] + 1 : Math.max(dp[(i + 1) * (m + 1) + j], dp[i * (m + 1) + j + 1]);
    let i = 0, j = 0, out = '';
    while (i < n && j < m) {
      if (A[i] === B[j]) { out += esc(A[i]); i++; j++; }
      else if (dp[(i + 1) * (m + 1) + j] >= dp[i * (m + 1) + j + 1]) { out += `<del>${esc(A[i])}</del>`; i++; }
      else { out += `<ins>${esc(B[j])}</ins>`; j++; }
    }
    while (i < n) out += `<del>${esc(A[i++])}</del>`;
    while (j < m) out += `<ins>${esc(B[j++])}</ins>`;
    return '<p>' + out.replace(/<\/del><del>/g, '').replace(/<\/ins><ins>/g, '').replace(/\n+/g, '</p><p>') + '</p>';
  }

  // ------------------------------------------------------------------ recherche
  function domFilter(i) { return st.domOn.has(st.idxRows[i].dom); }
  function codeHit(q) {
    const m = q.trim().match(/^(?:type\s+)?([a-z]{1,3})$/i); if (!m) return null;
    const c = m[1].toUpperCase();
    for (const dom of ORDRE_DOM) for (const g of st.plans[dom] || []) for (const t of g.tuiles) if (t.code === c && t.node && (dom === 'ERP' || /^[A-Z]{2,}$/.test(c))) return t;
    return null;
  }
  function directHit(q) {
    const m = q.match(/^\s*(?:art(?:icle)?\.?\s*)?([LRD]\.?\s?\d{3,4}(?:-\d+){1,2}|[A-Z]{1,3}\s?\d{1,3}(?:\s?bis)?|\d{1,3})\s*$/i);
    if (!m) return [];
    const k = S.normNum(m[1]);
    return (st.refGlobal.get(k) || []).filter((n) => st.domOn.has(n.dom));
  }
  function rank(q) {
    const { terms, recognized } = S.buildQuery(q, st.syn);
    const sc = st.index.score(terms, domFilter);
    const ids = []; for (let i = 0; i < sc.length; i++) if (sc[i] > 0) ids.push(i);
    ids.sort((a, b) => sc[b] - sc[a]);
    return { ids, sc, terms, recognized };
  }
  function hitHTML(n, terms, nSent = 1) {
    const nc = (st.cmtBy.get(n.row) || []).length;
    const body = n.type === 'Article' ? S.snippet(n.texte || n.fut, terms, 300, nSent) : S.highlight(n.titre, terms);
    return `<div class="hit dom-${n.dom}"><button class="plate" data-open="${n.id}">${n.type === 'Article' ? esc(dispNum(n)) : '§'}</button>
      <div><div class="where">${esc(DOMAINES[n.dom].court)} › ${esc(n.chemin.split(' › ').slice(-2).join(' › '))}</div>
      <div class="snip">${body}</div>
      <div class="meta">${n.futDate ? `<span class="pill warn">Modifié au ${fmtDate(n.futDate)}</span>` : ''}${nc ? `<span class="pill">💬 ${nc}</span>` : ''}${n.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}</div></div></div>`;
  }
  function renderSearch(q) {
    setSide(false);
    $('#read').className = 'pane readpane';
    if (!q.trim()) return renderHome();
    const direct = directHit(q);
    const ch = codeHit(q);
    const r = rank(q);
    const shown = r.ids.slice(0, 50);
    $('#read').innerHTML = `<div class="results">
      ${ch ? `<div class="jump dom-ERP"><span class="bigplate sm">${esc(ch.code)}</span><div><b>${esc(ch.label)}</b><div class="hint" style="margin:0">${esc(rangeTxt(ch))} · ${ch.arts} articles</div></div><button class="btn" data-open="${ch.node}" style="margin-left:auto">Ouvrir le chapitre</button></div>` : ''}
      ${direct.map((n) => `<div class="jump dom-${n.dom}"><button class="plate" style="position:static;width:auto" data-open="${n.id}">${esc(dispNum(n))}</button><div><b>${esc(DOMAINES[n.dom].label)}</b><div class="hint" style="margin:0">${esc(n.chemin.split(' › ').slice(-1)[0])}</div></div><button class="btn" data-open="${n.id}" style="margin-left:auto">Ouvrir</button></div>`).join('')}
      <h1>${r.ids.length ? r.ids.length.toLocaleString('fr-FR') + ' résultat' + (r.ids.length > 1 ? 's' : '') : 'Aucun résultat'} pour « ${esc(q)} »</h1>
      <p class="hint">${r.recognized.length ? 'Termes associés inclus : ' + r.recognized.map((x) => esc(x.group.key)).join(', ') + '. ' : ''}Passez en mode « Question » pour une réponse guidée.</p>
      ${shown.map((i) => hitHTML(st.idxRows[i], r.terms)).join('')}
      ${!r.ids.length ? '<p class="empty">Essayez un terme plus général, un synonyme, ou réactivez toutes les réglementations dans les filtres.</p>' : ''}
    </div>`;
    $('#read').scrollTop = 0;
  }

  // ------------------------------------------------------------------ « question » : recherche guidée
  const TYPE_LETTRES = 'JLMNOPRSTUVWXY'.split('');
  function understand(q, recognized) {
    const f = S.fold(q);
    const dom = [];
    if (/\b(erp|etablissement recevant|recevant du public)\b/.test(f)) dom.push('ERP');
    if (/\b(igh|grande hauteur)\b/.test(f)) dom.push('IGH');
    if (/\b(habitation|logement|immeuble d habitation|1re famille|2e famille|3e famille|4e famille)\b/.test(f)) dom.push('HAB');
    if (/\b(travail|employeur|salarie|travailleur|bureau)\b/.test(f)) dom.push('CDT');
    const types = new Set();
    const mt = q.match(/\btype\s+([JLMNOPRSTUVWXY])\b/gi) || [];
    mt.forEach((x) => types.add(x.slice(-1).toUpperCase()));
    for (const r of recognized) { const m = r.group.key.match(/^type ([A-Z])$/); if (m) types.add(m[1]); }
    if (types.size && !dom.includes('ERP')) dom.push('ERP');
    const cat5 = /\b(5e|5eme|cinquieme)\s+categorie\b|\bpetits? etablissements?\b/.test(f);
    const notions = recognized.filter((r) => !/^type /.test(r.group.key)).map((r) => r.group.key);
    return { dom, types: [...types], cat5, notions };
  }
  function boost(n, u) {
    let k = 1;
    if (u.dom.length) k *= u.dom.includes(n.dom) ? 1.35 : 0.55;
    if (u.types.length && n.dom === 'ERP') {
      const p = (n.num.match(/^[A-Z]+/) || [''])[0];
      if (u.types.includes(p)) k *= 1.9;
      else if (TYPE_LETTRES.includes(p)) k *= 0.35;
    }
    if (n.dom === 'ERP') { const p = (n.num.match(/^[A-Z]+/) || [''])[0]; if (u.cat5) k *= p === 'PE' ? 1.8 : 0.8; else if (p === 'PE') k *= 0.7; }
    if (n.type !== 'Article') k *= 0.5;
    return k;
  }
  let askSeq = 0;
  async function renderAsk(q) {
    setSide(false);
    $('#read').className = 'pane readpane';
    if (!q.trim()) return renderHome();
    const seq = ++askSeq;
    const r = rank(q);
    const u = understand(q, r.recognized);
    const N = st.idxRows.length;
    let sem = null;
    if (st.semOn) {
      $('#read').innerHTML = `<div class="results"><p class="hint">Analyse de la question…</p></div>`;
      sem = await S.Semantic.scores(q, N).catch(() => null);
      if (seq !== askSeq) return;
    }
    const maxB = r.ids.length ? r.sc[r.ids[0]] : 1;
    const cand = new Map();
    r.ids.slice(0, 400).forEach((i) => cand.set(i, (r.sc[i] / maxB) * (sem ? 0.5 : 1)));
    if (sem) {
      const idx = []; for (let i = 0; i < N; i++) if (domFilter(i)) idx.push(i);
      idx.sort((a, b) => sem[b] - sem[a]);
      const top = sem[idx[0]] || 1, floor = sem[idx[Math.min(300, idx.length - 1)]] || 0;
      idx.slice(0, 300).forEach((i) => cand.set(i, (cand.get(i) || 0) + 0.5 * Math.max(0, (sem[i] - floor) / (top - floor || 1))));
    }
    const ranked = [...cand.entries()].map(([i, s]) => [i, s * boost(st.idxRows[i], u)]).sort((a, b) => b[1] - a[1]).map((x) => st.idxRows[x[0]]).filter((n) => n.type === 'Article');
    const top = ranked.slice(0, 5), next = ranked.slice(5, 15);
    const futs = top.filter((n) => n.futDate);
    const pills = [
      ...u.dom.map((d) => `<span class="pill">${esc(DOMAINES[d].label)}</span>`),
      ...u.types.map((t) => `<span class="pill">ERP type ${t}</span>`),
      ...(u.cat5 ? ['<span class="pill">5e catégorie</span>'] : []),
      ...u.notions.map((x) => `<span class="pill">${esc(x)}</span>`),
    ];
    const llm = store.get('llm', {});
    $('#read').innerHTML = `<div class="results">
      <div class="answer">
        <h2>${top.length ? 'Articles à lire en priorité' : 'Aucun article ne correspond'}</h2>
        ${pills.length ? `<div class="understood"><span class="hint" style="margin:0">Compris :</span>${pills.join('')}</div>` : ''}
        <div id="gen"></div>
        <ol>${top.map((n) => `<li class="dom-${n.dom}"><b><button class="ref" data-ref="${n.id}" data-open="${n.id}" style="cursor:pointer">${esc(dispNum(n))}</button></b> <span class="hint">— ${esc(n.chemin.split(' › ').slice(-1)[0])}</span><div class="snip">${S.snippet(n.texte || n.fut, r.terms, 260, 2)}</div>${n.futDate ? `<span class="pill warn">Nouvelle rédaction au ${fmtDate(n.futDate)}</span>` : ''}</li>`).join('')}</ol>
        ${futs.length ? `<p class="pill warn" style="white-space:normal">Attention : ${futs.map(dispNum).join(', ')} ${futs.length > 1 ? 'vont changer' : 'va changer'} prochainement. Vérifiez la date de dépôt de votre dossier.</p>` : ''}
        <p class="disclaim">Extraits tirés des textes officiels, classés par pertinence. ${st.semOn ? 'Recherche par le sens activée.' : 'Activez la recherche sémantique dans les réglages pour mieux comprendre les questions formulées librement.'} Lisez toujours l'article complet avant de conclure.</p>
      </div>
      ${next.length ? `<h1 style="font-size:16px">Pour aller plus loin</h1>${next.map((n) => hitHTML(n, r.terms)).join('')}` : ''}
    </div>`;
    $('#read').scrollTop = 0;
    if (llm.url && llm.key && top.length) generate(q, top, seq);
  }

  async function generate(q, arts, seq) {
    const llm = store.get('llm', {});
    const box = $('#gen');
    box.innerHTML = '<p class="hint">Rédaction de la réponse…</p>';
    const ctx = arts.map((n) => `[${dispNum(n)}] (${DOMAINES[n.dom].label} — ${n.chemin.split(' › ').slice(-1)[0]})\n${(n.texte || n.fut).slice(0, 3500)}`).join('\n\n');
    try {
      const r = await fetch(llm.url, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + llm.key },
        body: JSON.stringify({
          model: llm.model, temperature: 0.1, messages: [
            { role: 'system', content: "Tu es un assistant en réglementation de sécurité incendie (France). Réponds uniquement à partir des extraits fournis, en français, en citant les articles entre crochets, ex. [CO 15]. Si les extraits ne suffisent pas, dis-le clairement. Sois concis." },
            { role: 'user', content: `Extraits :\n${ctx}\n\nQuestion : ${q}` },
          ],
        }),
      });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const d = await r.json();
      if (seq !== askSeq) return;
      const txt = d.choices[0].message.content;
      box.innerHTML = `<div class="gen legal">${esc(txt).replace(/\[([^\]]{1,20})\]/g, (m, x) => { const k = st.refGlobal.get(S.normNum(x.replace(/^Art\.\s*/, ''))); return k ? `<button class="ref" data-ref="${k[0].id}" data-open="${k[0].id}" style="cursor:pointer">[${esc(x)}]</button>` : m; })}</div>`;
    } catch (e) { box.innerHTML = `<p class="hint">Le LLM n'a pas répondu (${esc(e.message)}). Les articles ci-dessous restent valables.</p>`; }
  }

  // ------------------------------------------------------------------ veille
  st.vf = { statut: 'À lire', nature: '' };
  function renderVeille() {
    setSide(false);
    $('#read').className = 'pane readpane';
    const natures = ['Modification', 'Nouvel article', 'Abrogation', 'Modification à venir', 'Parution SiteSecurite'];
    const items = st.veille.filter((v) => (!st.vf.statut || v.statut === st.vf.statut) && (!st.vf.nature || v.nature === st.vf.nature) && (st.domOn.has(v.dom) || v.dom === 'Divers'));
    const counts = { 'À lire': st.veille.filter((v) => v.statut === 'À lire').length };
    let lastDay = '', h = '';
    for (const v of items.slice(0, 200)) {
      if (v.date !== lastDay) { lastDay = v.date; h += `<div class="vday">${fmtDate(v.date) || 'Sans date'}</div>`; }
      const n = st.byRow.get(v.art);
      h += `<div class="vitem dom-${DOMAINES[v.dom] ? v.dom : 'ERP'}${v.statut !== 'À lire' ? ' lu' : ''}" data-v="${v.row}">
        <header><span class="pill${/venir/.test(v.nature) ? ' warn' : ''}">${esc(v.nature)}</span><h3>${esc(v.titre)}</h3><span class="hint" style="margin:0">${esc(v.statut)}</span></header>
        ${v.source ? `<p class="src">${esc(v.source)}</p>` : ''}
        ${v.effet ? `<p class="src">Date d'effet : <b>${fmtDate(v.effet)}</b></p>` : ''}
        <div class="acts">
          ${n ? `<button data-open="${n.id}">Lire l'article</button>` : ''}
          ${v.ancien || v.nouveau ? `<button data-vdiff="${v.row}">Voir les changements</button>` : ''}
          ${v.lien ? `<a href="${esc(v.lien)}" target="_blank" rel="noopener">Source ↗</a>` : ''}
          ${v.statut === 'À lire' ? `<button data-vset="${v.row}" data-s="Lu">Marquer comme lu</button>` : `<button data-vset="${v.row}" data-s="À lire">Remettre à lire</button>`}
          <button data-vimpact="${v.row}">Analyser l'impact</button>
        </div>
        <div class="vx"></div></div>`;
    }
    $('#read').innerHTML = `<div class="veille"><h1>Veille réglementaire</h1>
      <p class="hint">Chaque modification publiée au Journal officiel est détectée automatiquement dans les textes suivis, avec le texte avant et après. Les parutions annoncées par SiteSecurite.com sont ajoutées en complément.</p>
      <div class="filters">
        ${['À lire', 'Lu', 'Impact analysé', ''].map((s) => `<button class="chip" aria-pressed="${st.vf.statut === s}" data-vf="statut" data-val="${s}">${s || 'Tout'}${s === 'À lire' ? ` (${counts['À lire']})` : ''}</button>`).join('')}
        <span style="width:10px"></span>
        ${['', ...natures].map((s) => `<button class="chip" aria-pressed="${st.vf.nature === s}" data-vf="nature" data-val="${s}">${s || 'Toutes natures'}</button>`).join('')}
      </div>
      ${h || '<p class="empty">Rien à lire : la veille est à jour.</p>'}</div>`;
    $('#read').scrollTop = 0;
  }
  async function setVeille(row, fields) {
    const v = st.veille.find((x) => x.row === row);
    const ok = await act([['UpdateRecord', 'REG_Veille', row, fields]]);
    if (ok) { if (fields.Statut) v.statut = fields.Statut; if ('Analyse' in fields) v.analyse = fields.Analyse; updateBadge(); renderVeille(); }
  }
  function updateBadge() {
    const n = st.veille.filter((v) => v.statut === 'À lire').length;
    const b = $('#veilleBadge'); b.hidden = !n; b.textContent = n > 99 ? '99+' : n;
  }

  // ------------------------------------------------------------------ événements globaux
  document.addEventListener('click', async (e) => {
    const t = e.target.closest('button, a, img[data-zoom], .lightbox'); if (!t) { if (!e.target.closest('#pop')) hidePop(); return; }
    const d = t.dataset;
    if (t.matches('img[data-zoom]')) { const lb = $('#lightbox'); $('img', lb).src = t.src; lb.classList.add('show'); return; }
    if (t.matches('.lightbox')) { t.classList.remove('show'); return; }
    if (d.ref && !d.open) { e.preventDefault(); showPop(t); return; }
    if (d.board) { go({ v: 'board', dom: d.board }); return; }
    if (d.gosec) { scrollToItem(d.gosec, true); return; }
    if (d.goart) { scrollToItem(d.goart); return; }
    if (d.href) { window.open(d.href, '_blank', 'noopener'); return; }
    if (d.open) { hidePop(); openNode(d.open); return; }
    if (d.tog) { st.expanded.has(d.tog) ? st.expanded.delete(d.tog) : st.expanded.add(d.tog); renderTree(); return; }
    if (d.focus) { st.pinActive = Date.now() + 1500; setActive(st.byId.get(d.focus), d.tab || st.sideTab); $('#side').classList.add('open'); if (d.tab === 'cmt') setTimeout(() => { const ta = $('#cform textarea'); ta && ta.focus(); }, 50); return; }
    if (d.stab) { st.sideTab = d.stab; renderSide(); return; }
    if (d.pin) { if (!st.pins.includes(d.pin)) st.pins.unshift(d.pin); hidePop(); st.sideTab = 'pins'; if (!st.active) st.active = st.byId.get(d.pin); setSide(true); renderSide(); $('#side').classList.add('open'); toast('Article épinglé'); return; }
    if (d.unpin) { st.pins = st.pins.filter((x) => x !== d.unpin); renderSide(); return; }
    if (d.untag) { const n = st.active; const tags = n.tags.filter((x) => x !== d.untag); if (await act([['UpdateRecord', 'REG_Articles', n.row, { Mots_cles: ['L', ...tags] }]])) { n.tags = tags; renderSide(); refreshArticle(n); } return; }
    if (d.copy) { const n = st.byId.get(d.copy); const ref = `${dispNum(n)} — ${n.chemin.split(' › ')[0]}`; try { await navigator.clipboard.writeText(ref); toast('Référence copiée'); } catch (err) { toast(ref); } return; }
    if (d.ss) { const n = st.byId.get(d.ss); try { await navigator.clipboard.writeText(dispNum(n)); } catch (err) { /* presse-papiers indisponible */ } window.open(ssPortal(n.dom), '_blank', 'noopener'); toast(`${dispNum(n)} copié : collez-le dans la recherche SiteSecurite`); return; }
    if (d.vf) { st.vf[d.vf] = d.val; renderVeille(); return; }
    if (d.vset) { setVeille(+d.vset, { Statut: d.s }); return; }
    if (d.vdiff) { const v = st.veille.find((x) => x.row === +d.vdiff); const box = $('.vx', t.closest('.vitem')); box.innerHTML = box.innerHTML ? '' : `<div class="diff legal">${v.ancien && v.nouveau ? diffHTML(v.ancien, v.nouveau) : v.nouveau ? `<ins>${esc(v.nouveau)}</ins>` : `<del>${esc(v.ancien)}</del>`}</div>`; return; }
    if (d.vimpact) { const v = st.veille.find((x) => x.row === +d.vimpact); const box = $('.vx', t.closest('.vitem')); box.innerHTML = `<textarea aria-label="Analyse d'impact" placeholder="Conséquences pour vos dossiers, établissements concernés…">${esc(v.analyse)}</textarea><div style="display:flex;justify-content:flex-end;margin-top:6px"><button class="btn" data-vsave="${v.row}">Enregistrer l'analyse</button></div>`; $('textarea', box).focus(); return; }
    if (d.vsave) { const ta = $('textarea', t.closest('.vitem')); setVeille(+d.vsave, { Analyse: ta.value, Statut: 'Impact analysé' }); return; }
    if (d.dom) { st.domOn.has(d.dom) ? st.domOn.delete(d.dom) : st.domOn.add(d.dom); if (!st.domOn.size) ORDRE_DOM.forEach((x) => st.domOn.add(x)); store.set('dom', [...st.domOn]); renderChips(); go(st.view, false); return; }
  });
  document.addEventListener('keydown', (e) => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
    if (e.key === 'Escape') { hidePop(); $('#lightbox').classList.remove('show'); $('#tree').classList.remove('open'); $('#side').classList.remove('open'); }
    if (typing) return;
    if (e.key === '/' || (e.key === 'k' && (e.ctrlKey || e.metaKey))) { e.preventDefault(); $('#q').focus(); $('#q').select(); }
    if ((e.key === 'j' || e.key === 'k') && st.view.v === 'read' && st.active) {
      const arts = [...document.querySelectorAll('.art')]; const i = arts.findIndex((a) => a.dataset.art === st.active.id);
      const nx = arts[i + (e.key === 'j' ? 1 : -1)]; if (nx) { st.pinActive = Date.now() + 800; nx.scrollIntoView({ block: 'start' }); setActive(st.byId.get(nx.dataset.art)); }
    }
  });

  // recherche
  const q = $('#q');
  const live = debounce(() => { if (st.mode === 'search') { if (q.value.trim()) go({ v: 'search', q: q.value }, false); } }, 200);
  q.addEventListener('input', live);
  q.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    e.preventDefault();
    live.cancel();
    if (!q.value.trim()) return;
    const ch = st.mode === 'search' ? codeHit(q.value) : null;
    if (ch) { openNode(ch.node); return; }
    const direct = st.mode === 'search' ? directHit(q.value) : [];
    if (direct.length === 1) { openNode(direct[0].id); return; }
    go({ v: st.mode === 'ask' ? 'ask' : 'search', q: q.value });
  });
  function setMode(m) {
    st.mode = m;
    $('#mSearch').setAttribute('aria-pressed', m === 'search'); $('#mAsk').setAttribute('aria-pressed', m === 'ask');
    q.placeholder = m === 'ask' ? 'Posez votre question, ex. : largeur des dégagements dans un ERP de type L' : "Mot-clé, n° d'article (CO 15, R. 4227-28) ou question…";
    q.focus();
  }
  $('#mSearch').onclick = () => setMode('search');
  $('#mAsk').onclick = () => setMode('ask');
  $('#btnHome').onclick = () => { q.value = ''; go({ v: 'home' }); };
  $('#btnVeille').onclick = () => go({ v: 'veille' });
  $('#btnTree').onclick = () => $('#tree').classList.toggle('open');
  $('#btnSide').onclick = () => $('#side').classList.toggle('open');

  function renderChips() {
    $('#domChips').innerHTML = ORDRE_DOM.filter((d) => st.nodes.some((n) => n.dom === d)).map((d) => `<button class="chip dom-${d}" data-dom="${d}" aria-pressed="${st.domOn.has(d)}" title="${esc(DOMAINES[d].label)}"><span class="dot"></span>${esc(DOMAINES[d].court)}</button>`).join('');
  }

  // réglages
  const dlg = $('#settings');
  $('#btnSettings').onclick = () => {
    const llm = store.get('llm', {});
    $('#optSem').checked = st.semOn; $('#optTheme').value = store.get('theme', '');
    $('#optUrl').value = llm.url || ''; $('#optModel').value = llm.model || ''; $('#optKey').value = llm.key || '';
    dlg.showModal();
  };
  $('#setCancel').onclick = () => dlg.close();
  $('#setSave').onclick = () => {
    store.set('llm', { url: $('#optUrl').value.trim(), model: $('#optModel').value.trim(), key: $('#optKey').value.trim() });
    const th = $('#optTheme').value; store.set('theme', th); applyTheme(th);
    const want = $('#optSem').checked; store.set('sem', want); dlg.close();
    if (want && !st.semOn) enableSemantic(); else if (!want) st.semOn = false;
  };
  function applyTheme(th) { if (th) document.documentElement.dataset.theme = th; else delete document.documentElement.dataset.theme; }

  async function enableSemantic() {
    const nvec = st.idxDocs.filter((d) => d.vec).length;
    if (!nvec) { toast("Les vecteurs sémantiques ne sont pas encore calculés dans ce document."); return; }
    toast('Téléchargement du modèle sémantique…');
    S.Semantic.onProgress = (p) => { if (p < 1) $('#toast').textContent = `Téléchargement du modèle : ${Math.round(p * 100)} %`; };
    await S.Semantic.enable(st.idxDocs);
    if (S.Semantic.state === 'ready') { st.semOn = true; toast(`Recherche sémantique prête (${S.Semantic.count} articles)`); }
    else { st.semOn = false; toast('Modèle indisponible : ' + (S.Semantic.error || 'réseau bloqué')); }
  }

  // ------------------------------------------------------------------ démarrage
  async function reload() {
    const data = await fetchAll();
    const keep = st.active && st.active.id;
    ingest(data);
    buildPlans();
    if (keep) st.active = st.byId.get(keep);
    updateBadge(); renderChips();
    if (st.view && st.view.v === 'read' && st.active) { renderSide(); refreshArticle(st.active); } else if (st.view && st.view.v === 'veille') renderVeille();
  }

  function showInstall(missing) {
    $('#main').classList.add('noside');
    $('#read').innerHTML = `<div class="results"><div class="answer">
      <h2>Installer la réglementation dans ce document</h2>
      <p>Le widget va créer ${missing.length} tables préfixées <b>REG_</b> (${missing.map(esc).join(', ')}), puis y charger les textes officiels à jour. Aucune table existante n'est modifiée. Comptez une à deux minutes.</p>
      <p class="hint">Il faut avoir le droit de modifier la structure du document (propriétaire ou éditeur).</p>
      <button class="btn" id="btnInstall">Installer et charger les textes</button>
      <div id="instState" class="semstate" style="margin-top:12px"></div></div></div>`;
    $('#btnInstall').onclick = async () => {
      $('#btnInstall').disabled = true;
      const stt = $('#instState');
      try {
        stt.textContent = 'Création des tables…';
        const syn = await fetch('data/synonymes.json').then((r) => r.json()).catch(() => ({}));
        await RegSync.install(st.ad, syn);
        await runUpdate(true, (d, t) => { stt.innerHTML = `Chargement des textes : ${d} / ${t} <span class="progress"><i style="width:${Math.round(100 * d / t)}%"></i></span>`; });
        await boot();
      } catch (e) {
        console.error(e);
        stt.textContent = "L'installation a échoué : " + (e.message || e);
        $('#btnInstall').disabled = false;
      }
    };
  }

  /* Met à jour les tables REG_ depuis les textes publiés avec le widget (droits de l'agent connecté). */
  async function runUpdate(force, onProgress) {
    const r = await RegSync.update(st.ad, { force, onProgress });
    if (r.etat === 'maj' && !force) {
      const v = r.resultat.veille;
      toast(`Réglementation mise à jour${v ? ` : ${v} nouveauté${v > 1 ? 's' : ''} dans la veille` : ''}`);
    }
    return r;
  }

  async function boot() {
    if (!st.ss) st.ss = await fetch('data/sitesecurite.json').then((r) => r.json()).catch(() => null);
    ingest(await fetchAll());
    buildPlans();
    renderChips(); updateBadge();
    go({ v: 'home' }, false);
    try { history.replaceState({ v: 'home' }, ''); } catch (e) { /* ignoré */ }
  }

  async function start() {
    st.inGrist = !!(window.grist && window.self !== window.top);
    st.ad = st.inGrist ? RegSync.GristAdapter : RegSync.MemoryAdapter();
    applyTheme(store.get('theme', ''));
    const savedDom = store.get('dom', null); if (savedDom && savedDom.length) st.domOn = new Set(savedDom);
    try {
      if (st.inGrist) {
        grist.ready({ requiredAccess: 'full', allowSelectBy: false });
        grist.onRecords(debounce(() => { if (st.nodes.length) reload(); }, 800));
        const missing = await RegSync.missingTables(st.ad);
        if (missing.length) { showInstall(missing); return; }
        await boot();
        // vérification de la version publiée, en arrière-plan
        runUpdate(false).then((r) => { if (r.etat === 'maj') reload(); }).catch((e) => console.warn('mise à jour', e));
      } else {
        // démonstration hors Grist : document en mémoire, installé et chargé comme le vrai
        const syn = await fetch('data/synonymes.json').then((r) => r.json()).catch(() => ({}));
        await RegSync.install(st.ad, syn);
        await RegSync.update(st.ad, { force: true });
        await boot();
      }
    } catch (e) {
      console.error(e);
      $('#read').innerHTML = `<div class="results"><h1>Impossible de lire le document</h1><p>${st.inGrist ? "Vérifiez que le widget a l'accès complet au document : options du widget → Accès → Accès complet au document." : 'Données introuvables à côté du widget (dossier data/).'}</p><p class="hint">${esc(e.message || String(e))}</p></div>`;
      return;
    }
    if (store.get('sem', false)) enableSemantic();
  }
  start();
})();
