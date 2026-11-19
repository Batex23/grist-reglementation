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
    DOC: { label: 'Doctrine & guides', court: 'Doctrine & guides' },
  };
  const ORDRE_DOM = ['ERP', 'IGH', 'HAB', 'CDT', 'CCH', 'DOC'];
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
    if (n.dom === 'DOC') {
      if (n.type === 'Texte') return num;
      const d = st.byId.get(n.legitext);
      return `${d ? d.num + ' ' : ''}§${num.replace(/^p\. /, 'p.')}`;
    }
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

  // ------------------------------------------------------------------ agents (fiche du personnel, comme GPREV Connect)
  const AGENTS = {
    table: 'Personnel_du_GPREV', identite: 'Identite',
    email: ['mail', 'Mail', 'Email', 'email', 'E_mail', 'Courriel'],
    photo: ['Photo', 'URL_Avatar', 'Avatar', 'Photo_Agent', 'Photo_agent', 'Image'],
    prenom: ['Prenom', 'Prénom', 'Pr_nom'], nom: ['NOM', 'Nom', 'nom'], grade: ['Grade', 'grade'],
  };
  const normEmail = (v) => String(v || '').trim().toLowerCase();
  function refId(v) {
    if (v == null || v === '') return null;
    if (typeof v === 'number') return v || null;
    if (Array.isArray(v)) return v[0] === 'R' ? +v[2] || null : (typeof v[0] === 'number' ? v[0] : null);
    return /^\d+$/.test(String(v)) ? +v : null;
  }
  async function loadAgents() {
    st.agents = new Map(); st.agentByEmail = new Map(); st.me = null;
    let rows;
    try { rows = await st.ad.fetch(AGENTS.table); } catch (e) { return; }
    if (!rows.length) return;
    const pick = (list, keys) => list.find((c) => keys.includes(c));
    const cols = Object.keys(rows[0]);
    const ce = pick(AGENTS.email, cols), cp = pick(AGENTS.photo, cols), cpr = pick(AGENTS.prenom, cols), cn = pick(AGENTS.nom, cols), cg = pick(AGENTS.grade, cols);
    for (const r of rows) {
      const a = {
        id: r.id, prenom: String((cpr && r[cpr]) || '').trim(), nom: String((cn && r[cn]) || '').trim(), grade: String((cg && r[cg]) || '').trim(),
        email: ce ? normEmail(r[ce]) : '', photo: cp ? r[cp] : null,
      };
      st.agents.set(a.id, a);
      if (a.email) st.agentByEmail.set(a.email, a);
    }
    if (st.inGrist) { try { await token(); } catch (e) { /* photos en pièce jointe indisponibles */ } }
    // agent connecté : la table Identite de GPREV ne montre à chacun que sa propre ligne
    try {
      const idr = await st.ad.fetch(AGENTS.identite);
      if (idr.length === 1) {
        const r = idr[0];
        const em = normEmail(r[pick(AGENTS.email, Object.keys(r))]);
        st.me = st.agents.get(refId(r.Personnel)) || st.agentByEmail.get(em) || null;
      }
    } catch (e) { /* pas de table Identite : l'auteur sera reconnu après publication */ }
  }
  const agentName = (a) => (a ? `${a.grade} ${a.prenom} ${a.nom}`.replace(/\s+/g, ' ').trim() : '');
  function agentOf(c) { return (c.agentId && st.agents && st.agents.get(c.agentId)) || (c.email && st.agentByEmail && st.agentByEmail.get(c.email)) || null; }
  function photoUrl(a) {
    if (!a || a.photo == null || a.photo === '') return null;
    const v = a.photo;
    const ids = Array.isArray(v) ? (v[0] === 'L' ? v.slice(1) : v).filter((x) => typeof x === 'number') : typeof v === 'number' ? [v] : [];
    if (ids.length) return st.token ? `${st.token.baseUrl}/attachments/${ids[0]}/download?auth=${encodeURIComponent(st.token.token)}` : null;
    const s = String(v).trim();
    const drive = s.match(/drive\.google\.com\/(?:file\/d\/|open\?id=|uc\?(?:export=\w+&)?id=)([\w-]{20,})/);
    if (drive) return `https://drive.google.com/thumbnail?id=${drive[1]}&sz=w200`;
    return /^(https?:\/\/|data:image\/)/i.test(s) ? s : null;
  }
  const AV_COLORS = ['#4f46e5', '#7c3aed', '#db2777', '#dc2626', '#ea580c', '#16a34a', '#0891b2', '#2563eb', '#9333ea', '#0d9488'];
  /* Avatar : photo de l'agent, sinon ses initiales sur une couleur stable */
  function avatar(a, fallbackName, size = 34) {
    const nom = a ? `${a.prenom} ${a.nom}` : (fallbackName || '?');
    const parts = nom.trim().split(/\s+/).filter(Boolean);
    const ini = a ? ((a.prenom[0] || '') + (a.nom[0] || '')).toUpperCase() : ((parts[0] || '?')[0] + ((parts[1] || '')[0] || '')).toUpperCase();
    let h = 0; for (const ch of nom) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
    const url = photoUrl(a);
    return `<span class="av" style="width:${size}px;height:${size}px;font-size:${Math.round(size * 0.38)}px;background:${AV_COLORS[h % AV_COLORS.length]}" aria-hidden="true">${esc(ini || '?')}${url ? `<img src="${esc(url)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">` : ''}</span>`;
  }
  const authorName = (c) => agentName(agentOf(c)) || c.auteur || 'Agent';

  async function fetchAll() {
    await loadAgents();
    const get = async (name) => { try { return await st.ad.fetch(name); } catch (e) { console.warn(name, e); return []; } };
    const opt = async (name) => { try { return await st.ad.fetch(name); } catch (e) { return null; } };
    const [reg, com, vei, syn, par, sch] = await Promise.all([get('REG_Articles'), get('REG_Commentaires'), get('REG_Veille'), get('REG_Synonymes'), get('REG_Parametres'), opt('REG_Schemas')]);
    st.params = Object.fromEntries(par.map((p) => [p.Cle, p.Valeur]));
    return { reg, com, vei, syn, sch };
  }

  function ingest(data) {
    st.erpNum = null;
    const nodes = data.reg.filter((r) => r.Identifiant).map((r) => ({
      row: r.id, id: r.Identifiant, parent: r.Parent || '', type: r.Type, dom: r.Domaine || 'ERP', num: r.Numero || '',
      titre: r.Titre || '', chemin: r.Chemin || '', niveau: r.Niveau || 0, ordre: r.Ordre || 0, texte: r.Texte || '',
      html: r.Texte_HTML || '', nota: r.Nota || '', etat: r.Etat || '', depuis: gDate(r.En_vigueur_depuis), fin: gDate(r.Fin_de_vigueur),
      hist: parseJSON(r.Historique, []), fut: r.Version_a_venir || '', futHtml: r.Version_a_venir_HTML || '', futDate: gDate(r.Date_a_venir),
      futPar: parseJSON(r.A_venir_par, []), legitext: r.Texte_officiel || '', lien: r.Lien_Legifrance || '',
      tags: gList(r.Mots_cles), vec: r.Vecteur || '', derniere: gDate(r.Derniere_modif_texte), pages: r.Pages || '',
    })).filter((n) => n.etat !== 'ABROGE');
    nodes.forEach((n) => { if (!Array.isArray(n.hist)) n.hist = []; });
    nodes.sort((a, b) => a.ordre - b.ordre);
    st.nodes = nodes; st.byId.clear(); st.byRow.clear(); st.pos.clear(); st.kids.clear(); st.refLocal.clear(); st.refGlobal.clear();
    nodes.forEach((n, i) => {
      st.byId.set(n.id, n); st.byRow.set(n.row, n); st.pos.set(n.id, i);
      if (!st.kids.has(n.parent)) st.kids.set(n.parent, []);
      st.kids.get(n.parent).push(n);
      if (n.type === 'Article' && n.num && n.dom !== 'DOC') {
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
    buildCitations();
    st.veille = data.vei.map((v) => ({
      row: v.id, date: gDate(v.Date), dom: v.Domaine || 'Divers', nature: v.Nature || '', titre: v.Titre || '', art: v.Article || 0,
      ancien: v.Ancien_texte || '', nouveau: v.Nouveau_texte || '', source: v.Source || '', lien: v.Lien || '', effet: gDate(v.Date_effet),
      statut: v.Statut || 'À lire', analyse: v.Analyse || '',
    })).sort((a, b) => (b.date || '').localeCompare(a.date || '') || b.row - a.row);
    st.syn = new S.Synonyms(data.syn.filter((s) => s.Terme));
    buildIndex();
  }

  /* Renvois doctrine → règlement : les articles cités par chaque fiche (« Article M 2 »),
     pour afficher sur l'article « Commenté dans : Guide M §1.4 ». */
  function buildCitations() {
    st.citedBy = new Map();
    for (const n of st.nodes) {
      if (n.dom !== 'DOC' || n.type !== 'Article' || !n.texte) continue;
      const vus = new Set();
      REF_RX.lastIndex = 0;
      let m;
      while ((m = REF_RX.exec(n.texte))) {
        const t = resolveRef(m, n);
        if (!t || t.dom === 'DOC' || vus.has(t.id)) continue;
        vus.add(t.id);
        if (!st.citedBy.has(t.id)) st.citedBy.set(t.id, []);
        st.citedBy.get(t.id).push(n);
      }
    }
  }

  /* Doctrine : adresse d'un PDF / d'une image de page, relative au widget */
  const docSlug = (n) => (n.legitext || '').replace(/^DOC:/, '');
  const pageRange = (n) => { const m = (n.pages || '').match(/^(\d+)(?:-(\d+))?/); return m ? [+m[1], +(m[2] || m[1])] : null; };
  const pageImg = (n, p) => `documents/${encodeURIComponent(docSlug(n))}/p${String(p).padStart(3, '0')}.jpg`;
  const pagesLabel = (n) => { const r = pageRange(n); return r ? (r[1] > r[0] ? `p. ${r[0]} à ${r[1]}` : `p. ${r[0]}`) : ''; };
  const fmtMois = (d) => (d ? new Date(d + 'T12:00:00').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }) : '');

  function ingestComments(com) {
    st.comments = com.filter((c) => c.Article).map((c) => ({
      row: c.id, art: c.Article, type: c.Type || '', texte: c.Texte || '', images: gList(c.Images).concat(jsonList(c.Images_data)), auteur: c.Auteur || '',
      email: normEmail(c.Auteur_email), agentId: refId(c.Agent),
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
    st.idxPos = new Map(st.idxRows.map((n, i) => [n.id, i]));
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
    if (!st.inGrist || (typeof id === 'string' && id.startsWith('data:'))) return id; // URL locale (démo) ou image intégrée
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
  /* Image → data URL compressée, stockée dans une colonne texte : évite l'envoi REST des pièces jointes,
     refusé par le serveur Grist depuis l'origine du widget (CORS). */
  async function toDataURL(file, max = 1400) {
    const img = await createImageBitmap(file);
    const k = Math.min(1, max / Math.max(img.width, img.height));
    const c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
    const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, 0, 0, c.width, c.height);
    const jpg = c.toDataURL('image/jpeg', 0.84); const png = c.toDataURL('image/png');
    return png.length < jpg.length ? png : jpg;
  }
  async function ensureCol(table, col) {
    const cols = await st.ad.columns(table);
    if (!cols.has(col)) await st.ad.apply([['AddColumn', table, col, { type: 'Text', isFormula: false }]]);
  }
  const jsonList = (v) => { try { const x = JSON.parse(v || '[]'); return Array.isArray(x) ? x : []; } catch (e) { return []; } };
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
    $('#btnAppl').setAttribute('aria-current', view.v === 'appl' ? 'page' : 'false');
    if (view.v === 'home') renderHome();
    else if (view.v === 'board') renderBoard(view.dom);
    else if (view.v === 'read') renderRead(view.id, view.focus);
    else if (view.v === 'search') renderSearch(view.q);
    else if (view.v === 'ask') renderAsk(view.q);
    else if (view.v === 'veille') renderVeille();
    else if (view.v === 'planches') renderPlanches(view.q);
    else if (view.v === 'appl') renderAppl();
    else if (view.v === 'juris') renderJuris(view.q, view.sec, view.focus);
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
    // Doctrine & guides : une tuile par document, groupées par catégorie
    const docs = st.nodes.filter((n) => n.type === 'Texte' && n.dom === 'DOC');
    const cats = [...new Set(docs.map((d) => d.chemin || 'Autres documents'))];
    st.plans.DOC = cats.map((c) => ({
      groupe: c, tuiles: docs.filter((d) => (d.chemin || 'Autres documents') === c).map((d) => {
        const arts = descendants(d).filter((x) => x.type === 'Article');
        const t = { code: d.num || '§', label: d.titre, node: d.id, arts: arts.length, de: 0, a: 0, fut: 0, ss: null,
          range: [fmtMois(d.depuis), `${arts.length} fiche${arts.length > 1 ? 's' : ''}`].filter(Boolean).join(' · '), doc: true };
        st.tileOf.set(d.id, t);
        return t;
      }),
    }));
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
      if (dom === 'ERP' || dom === 'DOC') continue;
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
      ${dom === 'DOC' ? '' : `<a class="sslink" href="${esc(ssPortal(dom))}" target="_blank" rel="noopener">Portail ${esc(DOMAINES[dom].court)} sur SiteSecurite ↗</a>`}</div>
      <p class="hint">${dom === 'DOC' ? 'Guides et doctrines découpés en fiches : cliquez un document pour lire ses fiches à la suite, avec les pages du PDF. Les articles cités dans les fiches s’ouvrent au survol, et chaque article du règlement indique les fiches qui le commentent.' : `Cliquez un ${dom === 'ERP' ? 'code' : 'chapitre'} pour lire tous ses articles à la suite. Raccourci : tapez ${dom === 'ERP' ? '« CO », « L » ou « CO 15 »' : 'un numéro d’article'} dans la recherche puis Entrée.`}</p>
      ${plan.map((g) => `<section class="bgroup"><h2>${esc(g.groupe)}</h2><div class="tiles${dom === 'DOC' ? ' docs' : ''}">${g.tuiles.map((t) => tileHTML(t, dom)).join('')}</div></section>`).join('')}
      ${dom === 'DOC' ? '<p class="hint addoc">Pour ajouter un guide ou une doctrine : déposez le PDF dans le dossier <b>documents</b> du dépôt GitHub (et, si vous le souhaitez, une ligne dans <b>documents/catalogue.json</b> pour son code, sa catégorie et sa date). Il apparaîtra ici après la publication, découpé en fiches.</p>' : ''}
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
    const isDoc = n.dom === 'DOC';
    const pref = isDoc ? '' : t.prefix || (/^[A-Z]+$/.test(t.code) ? t.code : '');
    const ssPages = pref && st.ss && st.ss.erp ? st.ss.erp[pref] || [] : [];
    const toc = secs.map((sec) => {
      const a = [sec, ...descendants(sec)].filter((x) => x.type === 'Article');
      const nums = a.map(firstInt).filter(Boolean);
      const lo = Math.min(...nums), hi = Math.max(...nums);
      const pages = ssPages.filter((p) => p.de <= hi && p.a >= lo);
      const rng = isDoc ? (a.length ? `§${a[0].num}${a.length > 1 ? '–' + a[a.length - 1].num : ''}` : '') : (a.length ? (pref ? pref + ' ' : '') + lo + (hi !== lo ? '–' + hi : '') : '');
      return `<div class="tocitem"><button data-gosec="${sec.id}"><span class="trange">${esc(rng)}</span>${esc(sec.titre.replace(/^(section|sous-section|chapitre)\s+[^:]*:\s*/i, ''))}</button>${pages.length === 1 ? `<a href="${esc(pages[0].url)}" target="_blank" rel="noopener" class="ssmini" title="Ouvrir ${esc(pages[0].libelle)} sur SiteSecurite">SS ↗</a>` : ''}</div>`;
    }).join('');
    return `<header class="chap">
      <div class="chaptop"><span class="bigplate">${esc(t.code)}</span>
        <div class="chaptitle"><h1>${esc(t.label)}</h1>
          <p class="hint">${isDoc ? esc([n.nota, fmtMois(n.depuis)].filter(Boolean).join(' · ')) + ` · ${arts.length} fiche${arts.length > 1 ? 's' : ''}` : `${esc(n.titre)} · ${arts.length} article${arts.length > 1 ? 's' : ''}`}${t.fut ? ` · <b class="tfut">${t.fut} modifié${t.fut > 1 ? 's' : ''} prochainement</b>` : ''}</p>
          <div class="chapacts">
            ${t.ss ? `<a class="btn ghost" href="${esc(t.ss)}" target="_blank" rel="noopener">Ouvrir ${esc(t.code)} sur SiteSecurite ↗</a>` : ''}
            ${n.lien ? `<a class="btn ghost" href="${esc(n.lien)}" target="_blank" rel="noopener">${isDoc ? 'Ouvrir le PDF ↗' : 'Légifrance ↗'}</a>` : ''}
            <label class="goto">Aller à ${isDoc ? 'la fiche' : pref ? esc(pref) : 'l’article'} <input id="gotoNum" inputmode="decimal" placeholder="n°" aria-label="Numéro"></label>
          </div></div></div>
      ${toc ? `<div class="toc">${toc}</div>` : ''}
      <div class="numgrid big">${arts.map((a) => `<button data-goart="${a.id}" class="${a.futDate ? 'chg' : ''}" title="${esc(dispNum(a))}${a.futDate ? ' — modifié le ' + fmtDate(a.futDate) : ''}">${esc(isDoc ? a.num : dispNum(a).replace(/^Art\. /, ''))}</button>`).join('')}</div>
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
      h += `<details class="plan"${sel && sel.dom === d && !cur ? ' open' : ''}><summary>${d === 'DOC' ? 'Plan détaillé des documents' : 'Plan officiel des textes'}</summary><ul class="tree" role="tree">`;
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
    const rec = arts.filter((n) => n.depuis && n.dom !== 'DOC').sort((a, b) => b.depuis.localeCompare(a.depuis)).slice(0, 10);
    const lastCm = st.comments.slice(0, 8);
    const signs = ORDRE_DOM.filter((d) => st.domOn.has(d)).map((d) => {
      const a = arts.filter((n) => n.dom === d); if (!a.length) return '';
      const last = a.reduce((m, n) => (n.depuis > m ? n.depuis : m), '');
      const nf = a.filter((n) => n.futDate).length;
      const txt = st.nodes.find((n) => n.type === 'Texte' && n.dom === d);
      if (d === 'DOC') {
        const nd = st.nodes.filter((n) => n.type === 'Texte' && n.dom === 'DOC').length;
        return `<button class="sign dom-DOC" data-board="DOC"><b>Doctrine</b><span>Guides pratiques et doctrines</span>
          <small>${nd} document${nd > 1 ? 's' : ''} · ${a.length} fiches · reliées aux articles cités</small></button>`;
      }
      return `<button class="sign dom-${d}" data-board="${d}"><b>${esc(DOMAINES[d].court)}</b>
        <span>${esc(DOMAINES[d].label)}</span>
        <small>${a.length.toLocaleString('fr-FR')} articles · dernière modification ${fmtDate(last)}${nf ? ` · ${nf} à venir` : ''}</small></button>`;
    }).join('');
    const tools = [
      st.appl ? `<button class="tool" data-appl="1"><b>Réglementation applicable</b><span>effectif, dégagements, extraction par type et catégorie</span></button>` : '',
      st.illus && st.illus.length ? `<button class="tool" data-planches="1"><b>Schémas</b><span>${st.illus.length} planches illustrées</span></button>` : '',
      `<button class="tool" data-juris="1"><b>Jurisprudence ERP</b><span>décisions par thème</span></button>`,
    ].join('');
    const li = (n, sub) => `<li class="dom-${n.dom}"><button data-open="${n.id}"><span class="mini">${esc(dispNum(n).replace('Art. ', ''))}</span><span>${esc(n.chemin.split(' › ').slice(-1)[0] || '')}<span class="sub">${sub}</span></span></button></li>`;
    $('#read').innerHTML = `<div class="home">
      <h1>Réglementation sécurité incendie</h1>
      <p class="lead">Textes officiels consolidés (Légifrance)${st.params && st.params.base_legifrance ? `, à jour au ${fmtDate(st.params.base_legifrance)}` : ''}. Survolez une référence citée pour lire l'article sans quitter la page ; commentez et illustrez chaque article.</p>
      <div class="signs">${signs}</div>
      <div class="cols">
        <section><h2>Changements à venir</h2>${fut.length ? `<ul class="list">${fut.slice(0, 12).map((n) => li(n, 'Nouvelle rédaction au ' + fmtDate(n.futDate))).join('')}</ul>` : '<p class="hint">Aucune modification programmée.</p>'}</section>
        <section><h2>Modifiés récemment</h2><ul class="list">${rec.map((n) => li(n, 'En vigueur depuis le ' + fmtDate(n.depuis))).join('')}</ul></section>
        <section><h2>Derniers commentaires</h2>${lastCm.length ? `<ul class="list">${lastCm.map((c) => { const n = st.byRow.get(c.art); return n ? li(n, `<span class="hwho">${avatar(agentOf(c), c.auteur, 20)}<b>${esc(authorName(c))}</b></span> ${esc(c.texte.slice(0, 90))}`) : ''; }).join('')}</ul>` : '<p class="hint">Aucun commentaire pour l’instant. Ouvrez un article et ajoutez le premier.</p>'}</section>
      </div>
      <nav class="tools" aria-label="Outils">${tools}</nav></div>`;
    $('#read').scrollTop = 0;
  }

  // ------------------------------------------------------------------ planches illustrées (publiées avec le widget)
  function illusKey(dom, num) { return dom + ':' + String(num || '').replace(/\s+/g, ' ').trim().toUpperCase(); }
  function loadIllus(cat) {
    if (cat) st.illusBase = cat.fiches || [];
    st.illus = (st.illusBase || []).concat(st.userIllus || []);
    st.illusBy = new Map();
    for (const f of st.illus) for (const a of f.articles) {
      if (!st.illusBy.has(a)) st.illusBy.set(a, []);
      st.illusBy.get(a).push(f);
    }
  }
  function illusOf(n) { return (st.illusBy && n && n.type === 'Article' && st.illusBy.get(illusKey(n.dom, n.num))) || []; }
  function illusSrc(f) { return f.src || 'illustrations/' + f.image; }
  /* Articles saisis à la main (« CO 38, CO 36 ; GH 7 ») → clés DOM:NUM des articles trouvés */
  function parseArts(txt) {
    const out = []; const bad = [];
    for (const tok of String(txt || '').split(/[,;\n]+/).map((x) => x.trim()).filter(Boolean)) {
      REF_RX.lastIndex = 0; const m = REF_RX.exec(tok);
      let n = null;
      if (m) {
        const key = m[1] ? m[1] + m[2] : m[3] ? m[3] + m[4] + (m[5] ? m[5].toUpperCase() : '') : '';
        const g = key && st.refGlobal.get(key);
        if (g && g.length) n = g.find((x) => x.dom === 'ERP') || g[0];
      }
      if (n) { const k = illusKey(n.dom, n.num); if (!out.includes(k)) out.push(k); } else bad.push(tok);
    }
    return { keys: out, bad };
  }
  /* Schémas ajoutés par les agents (table REG_Schemas) : images chargées une fois en mémoire */
  async function loadUserIllus(rows) {
    st.hasSchemas = rows !== null;
    const list = [];
    for (const r of rows || []) {
      const ids = gList(r.Image).filter((x) => typeof x === 'number' || typeof x === 'string');
      if ((!ids.length && !r.Image_data) || !r.Titre) continue;
      let src = r.Image_data || '';
      if (!src) try { src = await attUrl(ids[0]); } catch (e) { /* image indisponible */ }
      if (!src) continue;
      list.push({ id: 'U' + r.id, row: r.id, titre: r.Titre, articles: parseArts(r.Articles).keys, legende: r.Legende || '', src, user: true,
        auteur: r.Auteur || '', email: normEmail(r.Auteur_email || ''), ecarts: [] });
    }
    st.userIllus = list;
    loadIllus(null);
  }
  function illusArts(f) {
    return f.articles.map((a) => { const [dom, num] = a.split(':'); return st.nodes.find((n) => n.type === 'Article' && n.dom === dom && illusKey(dom, n.num) === a); }).filter(Boolean);
  }
  function figHTML(n) {
    const fs = illusOf(n); if (!fs.length) return '';
    return `<div class="figs${fs.length > 1 ? ' multi' : ''}">${fs.map((f) => `<figure class="illus">
      <button class="illus-img" data-page="${esc(illusSrc(f))}" title="Agrandir la planche « ${esc(f.titre)} »"><img loading="lazy" src="${esc(illusSrc(f))}" alt="Planche illustrée : ${esc(f.titre)}"></button>
      <figcaption><b>${esc(f.titre)}</b> ${esc(f.legende || '')}<button class="linkish" data-focus="${n.id}" data-tab="cmt">${f.user ? 'Schéma ajouté par ' + esc(f.auteur || 'un agent') : 'Planche SDIS 33'}${f.fiche ? ' · fiche ' + esc(f.fiche) : ''}${f.ecarts && f.ecarts.length ? ' · ce qui a changé' : ''}</button></figcaption>
    </figure>`).join('')}</div>`;
  }
  function illusCardHTML(n) {
    return illusOf(n).map((f) => {
      const autres = illusArts(f).filter((a) => a.id !== n.id);
      const ag = f.user ? st.agentByEmail && st.agentByEmail.get(f.email) : null;
      return `<div class="cmt illus-card">${f.user ? avatar(ag, f.auteur, 36) : '<span class="av sdis" style="width:36px;height:36px;font-size:13px" aria-hidden="true">33</span>'}<div class="cbody">
        <div class="cname">${f.user ? `Schéma ajouté par ${esc(agentName(ag) || f.auteur || 'un agent')}` : 'Planche illustrée — Prévention SDIS 33'}</div>
        <div class="who"><span class="pill">Photo / schéma</span>${f.fiche ? `<span>Fiche ${esc(f.fiche)} actualisée</span>` : ''}</div>
        <button class="illus-img" data-page="${esc(illusSrc(f))}" title="Agrandir"><img src="${esc(illusSrc(f))}" alt="Planche illustrée : ${esc(f.titre)}"></button>
        <div class="txt"><b>${esc(f.titre)}.</b> ${esc(f.legende || '')}</div>
        ${autres.length ? `<div class="cited"><span class="nob">Aussi sur</span>${autres.map((a) => `<button class="docref dom-${a.dom}" data-open="${a.id}">${esc(dispNum(a))}</button>`).join('')}</div>` : ''}
        ${f.ecarts && f.ecarts.length ? `<details class="ecarts"><summary>Ce qui change par rapport à l'ancienne fiche</summary><ul>${f.ecarts.map((e) => `<li>${esc(e)}</li>`).join('')}</ul></details>` : ''}
        <a class="dl" href="${esc(illusSrc(f))}" download="${esc(f.id)}.${f.user ? 'jpg' : 'png'}">Télécharger l'image</a>
      </div></div>`;
    }).join('');
  }
  function renderPlanches(q) {
    setSide(false);
    const norm = (x) => S.fold(x);
    const qq = q ? norm(q) : '';
    const list = (st.illus || []).filter((f) => !qq || norm([f.titre, f.legende, f.fiche, f.auteur, ...f.articles].join(' ')).includes(qq));
    const nu = (st.userIllus || []).length;
    $('#read').innerHTML = `<div class="home planches">
      <div class="pl-head"><h1>Planches illustrées</h1><button class="btn primary" data-addschema="1">Ajouter un schéma</button></div>
      <p class="lead">Schémas isométriques actualisés selon le texte en vigueur${nu ? `, et ${nu} schéma${nu > 1 ? 's' : ''} ajouté${nu > 1 ? 's' : ''} par les agents` : ''}, rangés sur les articles qu'ils illustrent. Cliquez une planche pour lire l'article.</p>
      <input id="plq" type="search" placeholder="Filtrer : voie, escalier, CO 38, C.15…" value="${esc(q || '')}" aria-label="Filtrer les planches">
      <div class="pgrid">${list.map((f) => { const a = illusArts(f)[0]; return `<button class="pcard${f.user ? ' user' : ''}" ${a ? `data-open="${a.id}"` : `data-page="${esc(illusSrc(f))}"`}>
        <img loading="lazy" src="${esc(illusSrc(f))}" alt=""><span class="pt">${esc(f.titre)}</span>
        <span class="pr">${f.articles.map((x) => esc(x.split(':')[1])).join(' · ')}${f.fiche ? ` <em>fiche ${esc(f.fiche)}</em>` : ''}${f.user ? ` <em>par ${esc(f.auteur || 'un agent')}</em>` : ''}</span></button>`; }).join('') || '<p class="hint">Aucune planche ne correspond.</p>'}</div></div>`;
    const inp = $('#plq'); inp.addEventListener('input', debounce(() => { st.view.q = inp.value; renderPlanches(inp.value); const i = $('#plq'); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 250));
    $('#read').scrollTop = 0;
  }
  /* Formulaire « Ajouter un schéma » : image, titre, articles illustrés, légende */
  function addSchemaForm(pre) {
    let ov = $('#schemaForm');
    if (!ov) { ov = document.createElement('div'); ov.id = 'schemaForm'; ov.className = 'cpv'; document.body.append(ov); }
    ov.hidden = false;
    ov.innerHTML = `<form class="cpv-box sf" role="dialog" aria-modal="true" aria-label="Ajouter un schéma">
      <div class="cpv-head"><b>Ajouter un schéma</b><button type="button" class="x" data-sf="close" aria-label="Fermer">×</button></div>
      <p class="hint">Le schéma est enregistré dans le document Grist et s'affiche sur chaque article indiqué, dans la galerie et dans la réglementation applicable.</p>
      <label class="sf-drop" id="sfDrop"><input type="file" name="img" accept="image/*" hidden><span id="sfPrev">Déposez une image, collez-la (Ctrl+V) ou cliquez pour la choisir</span></label>
      <label>Titre<input name="titre" required maxlength="120" placeholder="Ex. : Recoupement des combles"></label>
      <label>Articles illustrés<input name="arts" required value="${esc(pre || '')}" placeholder="Ex. : CO 24, CO 25, GH 7"><span class="sf-arts" id="sfArts"></span></label>
      <label>Légende<textarea name="leg" rows="3" placeholder="Ce que montre le schéma, valeurs à retenir, source"></textarea></label>
      <div class="sf-go"><button type="button" class="btn ghost" data-sf="close">Annuler</button><button class="btn primary" type="submit">Enregistrer le schéma</button></div>
    </form>`;
    const f = $('form', ov); let file = null;
    const show = () => { $('#sfPrev').innerHTML = file ? `<img src="${URL.createObjectURL(file)}" alt="">` : 'Déposez une image, collez-la (Ctrl+V) ou cliquez pour la choisir'; };
    const arts = () => {
      const r = parseArts(f.arts.value);
      $('#sfArts').innerHTML = r.keys.map((k) => `<span class="ok">${esc(k.split(':')[1])}</span>`).join('') + r.bad.map((b) => `<span class="ko" title="Article introuvable">${esc(b)}</span>`).join('');
      return r;
    };
    arts();
    f.img.onchange = () => { file = f.img.files[0] || null; show(); };
    const drop = $('#sfDrop');
    ['dragover', 'dragenter'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
    ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove('over')));
    drop.addEventListener('drop', (e) => { e.preventDefault(); const x = [...e.dataTransfer.files].find((y) => y.type.startsWith('image/')); if (x) { file = x; show(); } });
    f.addEventListener('paste', (e) => { const x = [...((e.clipboardData || {}).files || [])].find((y) => y.type.startsWith('image/')); if (x) { file = x; show(); } });
    f.arts.addEventListener('input', arts);
    ov.onclick = (e) => { const b = e.target.closest('[data-sf]'); if ((b && b.dataset.sf === 'close') || e.target === ov) ov.hidden = true; };
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const r = arts();
      if (!file) { toast('Ajoutez une image'); return; }
      if (!r.keys.length) { toast('Indiquez au moins un article reconnu (ex. CO 38)'); return; }
      const btn = $('button[type=submit]', f); btn.disabled = true; btn.textContent = 'Enregistrement…';
      try {
        await RegSync.ensureOptional(st.ad, 'REG_Schemas');
        const rec = { Titre: f.titre.value.trim(), Articles: r.keys.map((k) => k.split(':')[1]).join(', '), Legende: f.leg.value.trim() };
        if (st.inGrist) { await ensureCol('REG_Schemas', 'Image_data'); rec.Image_data = await toDataURL(file, 1800); }
        else rec.Image = ['L', ...(await upload([file]))];
        const ok = await act([['AddRecord', 'REG_Schemas', null, rec]]);
        if (ok) { ov.hidden = true; toast('Schéma enregistré'); await reload(); if (st.view && st.view.v !== 'planches') go(st.view, false); }
        else { btn.disabled = false; btn.textContent = 'Enregistrer le schéma'; }
      } catch (err) { toast('Échec : ' + (err.message || err)); btn.disabled = false; btn.textContent = 'Enregistrer le schéma'; }
    });
    setTimeout(() => f.titre.focus(), 50);
  }

  // ------------------------------------------------------------------ jurisprudence
  /* Surligne les termes de la requête dans un bloc déjà rendu */
  function markTerms(el, terms) {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const todo = [];
    while (tw.nextNode()) if (!tw.currentNode.parentNode.closest('mark,button')) todo.push(tw.currentNode);
    for (const tn of todo) {
      const h = S.highlight(tn.nodeValue, terms);
      if (!h.includes('<mark>')) continue;
      const t = document.createElement('template'); t.innerHTML = h; tn.replaceWith(t.content);
    }
  }
  const jText = (d) => d.h.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
  function jurisIndex() {
    if (!st.juris || st.jIdx) return;
    st.jIdx = new S.Index(st.juris.decisions.map((d, i) => ({ key: i, fields: { num: '', path: d.s + ' ' + d.p, body: jText(d), extra: d.cite.join(' ') + ' ' + d.j } })));
  }
  /* Décisions classées pour une requête : [{i, sc}] */
  function jurisRank(terms) {
    if (!st.jIdx) return [];
    const sc = st.jIdx.score(terms);
    const out = []; for (let i = 0; i < sc.length; i++) if (sc[i] > 0) out.push({ i, sc: sc[i] });
    return out.sort((a, b) => b.sc - a.sc);
  }
  function jurisHitsHTML(q, terms, max) {
    if (!st.domOn.has('ERP')) return '';
    const hits = jurisRank(terms);
    if (!hits.length) return '';
    const J = st.juris.decisions;
    return `<section class="jhits"><h2>Jurisprudence <span class="hint">${hits.length} décision${hits.length > 1 ? 's' : ''}</span></h2>
      ${hits.slice(0, max).map(({ i }) => { const d = J[i]; return `<button class="jhit" data-jfocus="${i}" data-jq="${esc(q)}"><span class="jw">${esc(d.s || d.c)}${d.p ? ' › ' + esc(d.p.slice(0, 90)) + (d.p.length > 90 ? '…' : '') : ''}</span>
        <span class="snip">${S.snippet(jText(d), terms, 260, 1)}</span><span class="jref">${esc([d.j, d.d].filter(Boolean).join(', '))}</span></button>`; }).join('')}
      ${hits.length > max ? `<button class="linkish" data-jall="${esc(q)}">Voir les ${hits.length} décisions</button>` : ''}</section>`;
  }
  async function renderJuris(q, sec, focus) {
    setSide(false);
    if (!st.juris) st.juris = await fetch('data/jurisprudence.json', { cache: 'no-cache' }).then((r) => r.json()).catch(() => null);
    const J = st.juris;
    if (!J) { $('#read').innerHTML = '<div class="home"><p class="hint">Jurisprudence indisponible.</p></div>'; return; }
    const secs = [...new Set(J.decisions.map((d) => d.s).filter(Boolean))];
    jurisIndex();
    const qt = q && q.trim() ? S.buildQuery(q, st.syn).terms : null;
    const keep = qt ? new Set(jurisRank(qt).map((x) => x.i)) : null;
    const list = J.decisions.map((d, i) => Object.assign({ i }, d)).filter((d) => (!sec || d.s === sec) && (!keep || keep.has(d.i)));
    let lc = null, ls = null, lp = null;
    const body = list.map((d) => {
      let h = '';
      if (d.c !== lc) { h += `<h2 class="jc">${esc(d.c)}</h2>`; lc = d.c; ls = null; lp = null; }
      if (d.s !== ls) { if (d.s) h += `<h3 class="js">${esc(d.s)}</h3>`; ls = d.s; lp = null; }
      if (d.p && d.p !== lp) { h += `<p class="jp">${esc(d.p)}</p>`; lp = d.p; }
      return h + `<article class="jd${focus === d.i ? ' focus' : ''}" id="jd-${d.i}"><div class="legal jtxt">${d.h}</div>${d.cite.length ? `<footer>${d.j ? `<b>${esc(d.j)}</b>` : ''}${d.d ? `<span>${esc(d.d)}</span>` : ''}<span class="jfull">${esc(d.cite.join(' ; '))}</span></footer>` : ''}</article>`;
    }).join('');
    $('#read').className = 'pane readpane';
    $('#read').innerHTML = `<div class="home juris">
      <h1>Jurisprudence ERP</h1>
      <p class="lead">${J.decisions.length} décisions classées par thème : consultation et avis de la commission de sécurité, notion d'ERP, pouvoirs de police, responsabilités.</p>
      <input id="jq" type="search" placeholder="Filtrer : fermeture, permis de construire, 5e catégorie, association…" value="${esc(q || '')}" aria-label="Filtrer la jurisprudence">
      <div class="jchips"><button class="jchip" data-jsec="" aria-pressed="${!sec}">Tout</button>${secs.map((x) => `<button class="jchip" data-jsec="${esc(x)}" aria-pressed="${x === sec}">${esc(x)}</button>`).join('')}</div>
      <p class="hint">${list.length} décision${list.length > 1 ? 's' : ''}. ${esc(J.source)}.</p>
      ${body || '<p class="hint">Aucune décision ne correspond.</p>'}
    </div>`;
    document.querySelectorAll('.jtxt').forEach((el) => { linkify(el, { legitext: '' }); if (qt) markTerms(el, qt); });
    const inp = $('#jq'); inp.addEventListener('input', debounce(() => { st.view.q = inp.value; st.view.focus = null; renderJuris(inp.value, st.view.sec).then(() => { const i = $('#jq'); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }); }, 250));
    $('#read').scrollTop = 0;
    if (focus != null) { const el = $('#jd-' + focus); if (el) el.scrollIntoView({ block: 'center' }); }
  }

  // ------------------------------------------------------------------ réglementation applicable (extraction par type et catégorie)
  const CAT_LBL = { 1: '1re', 2: '2e', 3: '3e', 4: '4e', 5: '5e' };
  const NIVEAUX = [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const nivLbl = (n) => (n < 0 ? `SS${n}` : n === 0 ? 'RDC' : `R+${n}`);
  function applNode(num) {
    if (!st.erpNum) {
      st.erpNum = new Map();
      for (const n of st.nodes) if (n.type === 'Article' && n.dom === 'ERP' && !st.erpNum.has(n.num)) st.erpNum.set(n.num, n);
    }
    return st.erpNum.get(num);
  }
  function artTitle(n) {
    const t = ((n && n.texte) || '').split('\n')[0].trim();
    return t && t.length < 110 && !t.startsWith('§') ? t : (n ? n.chemin.split(' › ').slice(-1)[0].replace(/^(Section|Sous-section|Chapitre) [^:]*: /, '') : '');
  }

  /* --- état du calculateur (persistant) --- */
  function calcState() {
    if (st.calc) return st.calc;
    const A = st.appl;
    let c = store.get('applCalc', null);
    if (!c || !Array.isArray(c.types) || !c.types.length) {
      const old = store.get('appl', {});
      c = { types: [old.t || 'L'], variants: {}, rows: [], cat: null, sommeil: null, filtre: true };
    }
    c.types = c.types.filter((x) => A.types.some((t) => t.code === x));
    if (!c.types.length) c.types = ['L'];
    c.rows = (c.rows || []).filter((r) => r && typeof r === 'object');
    if (c.filtre == null) c.filtre = true;
    st.calc = c;
    return c;
  }
  const saveCalc = () => store.set('applCalc', st.calc);
  const typeOf = (code) => st.appl.types.find((t) => t.code === code);
  const methOf = (id) => st.appl.methodes.find((m) => m.id === id);
  function methLabel(m, niv) {
    if (m.o === 'niveau') return niv <= 1 ? '1 personne pour 3 m²' : niv === 2 ? '1 personne pour 6 m²' : '1 personne pour 15 m²';
    return m.lab;
  }
  function methK(m, niv) {
    if (m.o === 'niveau') return niv <= 1 ? 1 / 3 : niv === 2 ? 1 / 6 : 1 / 15;
    return m.k;
  }
  /* Effectifs d'une ligne : {pub, pers, calc (public calculé), cumul} */
  function rowEff(r) {
    const m = methOf(r.m);
    const q = parseFloat(String(r.q || '').replace(',', '.')) || 0;
    const calc = m ? Math.ceil(q * methK(m, +r.niv) - 1e-9) : 0;
    const persCalc = m && m.kp ? Math.ceil(q * m.kp - 1e-9) : 0;
    const pub = r.pub !== '' && r.pub != null ? (+r.pub || 0) : calc;
    const pers = r.pers !== '' && r.pers != null ? (+r.pers || 0) : persCalc;
    const ct = !!(m && m.o === 'ct');
    return { pub: ct ? 0 : pub, pers, calc: ct ? 0 : calc, persCalc, cumul: !(m && (m.o === 'noncumul' || ct)), ct, m };
  }
  function seuilNum(v) { const x = parseInt(v, 10); return isNaN(x) ? null : x; }
  /* Classement : catégorie calculée et justification */
  function classer() {
    const c = calcState();
    const rows = c.rows.filter((r) => r.m);
    if (!rows.length) return null;
    const per = {}; let pub = 0, pers = 0, ss = 0, et = 0; const lvEt = new Set();
    for (const r of rows) {
      const e = rowEff(r); if (!e.cumul) continue;
      const t = (e.m && e.m.t) || r.t;
      const p = (per[t] = per[t] || { pub: 0, ss: 0, et: 0, res: 0, lv: new Set(), bas: false });
      p.pub += e.pub; pub += e.pub; pers += e.pers;
      if (+r.niv <= 0) p.bas = true;
      if (+r.niv < 0) { p.ss += e.pub; ss += e.pub; }
      if (+r.niv > 0) { p.et += e.pub; et += e.pub; p.lv.add(+r.niv); lvEt.add(+r.niv); }
      if (e.m && e.m.o === 'res') p.res += e.pub;
    }
    const why = []; const alerts = [];
    // un type est-il, à lui seul, au 1er groupe (PE 2) ?
    const g1Type = {};
    for (const [code, p] of Object.entries(per)) {
      const t = typeOf(code); if (!t || !t.seuils.length) continue;
      const v = (t.var || [{ rows: t.seuils.map((_, i) => i) }])[c.variants[code] || 0] || { rows: [0] };
      for (const ri of v.rows) {
        const row = t.seuils[ri]; if (!row) continue;
        const sSS = seuilNum(row[1]), sEt = row[2].startsWith('1 (') ? (p.lv.size === 1 && !p.bas ? 20 : 1) : seuilNum(row[2]), sTot = seuilNum(row[3]);
        if (row[1] === 'interdit' && p.ss > 0) alerts.push(`${code} : ${row[0]} interdits en sous-sol (PE 2)`);
        const base = /résidents/.test(row[0]) ? p.res : p.pub;
        if (sTot != null && base >= sTot) { g1Type[code] = `${code} : ${/résidents/.test(row[0]) ? 'résidents' : 'public'} ${base} ≥ ${sTot} (PE 2, ${row[0].toLowerCase()})`; break; }
        if (sSS != null && p.ss >= sSS) { g1Type[code] = `${code} : public en sous-sol ${p.ss} ≥ ${sSS} (PE 2)`; break; }
        if (sEt != null && p.et >= sEt) { g1Type[code] = `${code} : public en étages ${p.et} ≥ ${sEt} (PE 2)`; break; }
      }
    }
    const types = Object.keys(per);
    let groupe1 = false;
    if (types.length > 1) {
      if (ss >= 50) why.push(`public en sous-sol ${ss} ≥ 50 (GN 2 § 2, types différents)`);
      if (et >= 100) why.push(`public en étages ${et} ≥ 100 (GN 2 § 2)`);
      if (pub >= 200) why.push(`public total ${pub} ≥ 200 (GN 2 § 2)`);
      for (const w of Object.values(g1Type)) why.push(`${w}, donc 4e catégorie au moins (GN 2 § 2)`);
      groupe1 = why.length > 0;
    } else {
      const w = Object.values(g1Type)[0];
      if (w) { why.push(w); groupe1 = true; }
      const t = typeOf(types[0]);
      if (t && !t.seuils.length) { why.push(`type ${t.code} : pas de seuil de 5e catégorie dans PE 2, classement selon R. 143-19`); groupe1 = true; }
    }
    let cat;
    if (!groupe1) {
      cat = 5;
      why.push(`public ${pub} sous les seuils ${types.length > 1 ? 'de GN 2 § 2 (50 en sous-sol, 100 en étages, 200 au total)' : 'du 1er groupe (PE 2)'} : 5e catégorie, le personnel n'intervient pas (GN 1 § 2 b)`);
    } else {
      const tot = pub + pers;
      cat = tot > 1500 ? 1 : tot > 700 ? 2 : tot > 300 ? 3 : 4;
      why.push(`effectif public ${pub} + personnel ${pers} = ${tot} : ${CAT_LBL[cat]} catégorie (R. 143-19)`);
    }
    return { cat, pub, pers, tot: pub + pers, ss, et, why, alerts, per };
  }
  function currentCat() {
    const c = calcState();
    if (c.cat) return c.cat;
    const r = classer();
    return r ? r.cat : 3;
  }

  /* --- filtrage par catégorie : passages et articles --- */
  const ORDW = { premi: 1, deuxi: 2, troisi: 3, quatri: 4, cinqui: 5 };
  const CAT_RX = /\b((?:[1-5](?:re|er|ère|e|ème)|premi[èe]re|deuxi[èe]me|troisi[èe]me|quatri[èe]me|cinqui[èe]me)(?:\s*(?:,|et|à|ou)\s*(?:de\s+)?(?:la\s+)?(?:[1-5](?:re|er|ère|e|ème)|premi[èe]re|deuxi[èe]me|troisi[èe]me|quatri[èe]me|cinqui[èe]me))*\s+cat[ée]gories?|(?:deux|trois|quatre) premi[èe]res cat[ée]gories)/gi;
  const NEG_RX = /(sauf|à l'exception|exception faite|excepté|autres? que|hormis|non applicables?|ne s'applique pas|ne sont pas applicables|dispensés?)[^.;]{0,50}$/i;
  const LIQ_RX = /(liquides?|combustibles?|alcools?|produits?|gaz)\s+(?:inflammables?\s+)?(?:de\s+)?(?:la\s+)?$/i;
  function catsIn(s) {
    if (/quatre premi/i.test(s)) return [1, 2, 3, 4];
    if (/trois premi/i.test(s)) return [1, 2, 3];
    if (/deux premi/i.test(s)) return [1, 2];
    const out = []; let range = false;
    for (const m of s.matchAll(/([1-5])(?:re|er|ère|e|ème)|(premi|deuxi|troisi|quatri|cinqui)[èe]|\s(à)\s/gi)) {
      if (m[3]) { range = true; continue; }
      const v = m[1] ? +m[1] : ORDW[S.fold(m[2])];
      if (!v) continue;
      if (range && out.length) { for (let i = out[out.length - 1] + 1; i <= v; i++) out.push(i); range = false; } else out.push(v);
    }
    return out;
  }
  /* Catégories visées par un texte (null si aucune). lead : seulement au début du texte */
  function scopeOf(txt, lead) {
    CAT_RX.lastIndex = 0; let m; let res = null;
    while ((m = CAT_RX.exec(txt))) {
      const before = txt.slice(Math.max(0, m.index - 60), m.index);
      if (LIQ_RX.test(before)) continue;
      if (lead && m.index > 110) break;
      let cs = catsIn(m[0]);
      if (NEG_RX.test(before)) cs = [1, 2, 3, 4, 5].filter((x) => !cs.includes(x));
      res = (res || []).concat(cs);
    }
    return res;
  }
  /* Applicabilité des lignes d'un texte : [{t, ok}] (ok null = neutre) */
  function blocksScope(lines, cat) {
    let scope = null;
    return lines.map((t) => {
      const s = t.trim();
      const head = /^(§|paragraphe|article|[IVX]+\.|\d+°)/i.test(s);
      const sc = scopeOf(s, true);
      if (sc) { scope = /:\s*$/.test(s) ? sc : null; return { t, ok: sc.includes(cat) }; }
      if (head) scope = null;
      if (scope && /^(-|–|•|[a-z]\)|\d+\))/.test(s)) return { t, ok: scope.includes(cat) };
      if (scope && !/^(-|–|•|[a-z]\)|\d+\))/.test(s)) scope = null;
      return { t, ok: null };
    });
  }
  /* L'article vise-t-il la catégorie ? true / false (exclu) */
  function artApplies(n, cat) {
    if (!n) return true;
    const key = n.id + ':' + cat;
    st.artCat = st.artCat || new Map();
    if (st.artCat.has(key)) return st.artCat.get(key);
    const lines = (n.texte || '').split('\n').filter((l) => l.trim());
    let ok = true;
    const tsc = lines.length ? scopeOf(lines[0], true) : null;
    if (tsc && lines[0].length < 140) ok = tsc.includes(cat);
    else if (lines.length > 1) {
      const b = blocksScope(lines.slice(1), cat);
      const scoped = b.filter((x) => x.ok !== null);
      if (scoped.length && scoped.length === b.length && scoped.every((x) => !x.ok)) ok = false;
    }
    st.artCat.set(key, ok);
    return ok;
  }
  /* Applique le filtre aux blocs rendus d'un article */
  function filterDom(el, cat, filtre) {
    const blocks = [...el.children].flatMap((b) => (b.tagName === 'TABLE' ? [...b.querySelectorAll('tr')] : [b]));
    const lines = blocks.map((b) => (b.tagName === 'TR' ? (b.cells[0] ? b.cells[0].textContent : '') : b.textContent));
    const sc = blocksScope(lines, cat);
    let hid = [];
    const flush = (after) => {
      if (!hid.length) return;
      const stub = document.createElement('p');
      stub.className = 'offstub';
      const n = hid.length; const grp = hid;
      const lab = `${n} passage${n > 1 ? 's' : ''} visant une autre catégorie, masqué${n > 1 ? 's' : ''} · afficher`;
      stub.textContent = lab;
      stub.onclick = () => { grp.forEach((b) => b.classList.remove('offcat')); stub.remove(); };
      grp[0].before(stub); hid = [];
    };
    sc.forEach((x, i) => {
      const b = blocks[i];
      if (x.ok === false && b.tagName === 'TR') { if (hid.length) flush(hid[0]); b.classList.add('offsoft'); return; }
      if (x.ok === false) { b.classList.add(filtre ? 'offcat' : 'offsoft'); if (filtre) hid.push(b); else flush(b); }
      else { if (hid.length) flush(hid[0]); if (x.ok) b.classList.add('oncat'); }
    });
    if (hid.length) flush(hid[0]);
  }
  function markCats(el, cat, eff) {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const todo = [];
    while (tw.nextNode()) todo.push(tw.currentNode);
    const RX = new RegExp(CAT_RX.source + '|(?:plus de|moins de|au moins|au-delà de|au-dessus de|supérieure? à|inférieure? à|jusqu\'à|à partir de)\\s+\\d[\\d\\s]*\\s(?:personnes|places)', 'gi');
    for (const tn of todo) {
      const s = tn.nodeValue; RX.lastIndex = 0; let m, last = 0, frag = null;
      while ((m = RX.exec(s))) {
        const isCat = /cat[ée]gorie/i.test(m[0]);
        if (isCat && LIQ_RX.test(s.slice(Math.max(0, m.index - 60), m.index))) continue;
        frag = frag || document.createDocumentFragment();
        frag.append(s.slice(last, m.index));
        const mk = document.createElement('mark');
        if (isCat) mk.className = 'catm' + (catsIn(m[0]).includes(cat) ? ' on' : '');
        else { mk.className = 'effm'; if (eff) mk.title = `Effectif calculé de l'établissement : ${eff} personnes`; }
        mk.textContent = m[0]; frag.append(mk); last = m.index + m[0].length;
      }
      if (frag) { frag.append(s.slice(last)); tn.replaceWith(frag); }
    }
  }

  /* --- rubriques fusionnées pour plusieurs types --- */
  function applRows(codes, cat, sommeil) {
    const A = st.appl;
    const ts = codes.map(typeOf).filter(Boolean);
    const anyII = ts.some((t) => t.livre === 'II');
    const g2 = cat === 5;
    const base = anyII ? (g2 ? A.rub2 : A.rub1) : A.rub1;
    const rows = base.map((r) => ({ c: r.c, id: r.id, t: r.t, dg: anyII ? r.dg.concat(g2 && sommeil ? (A.sommeil[r.id] || []) : []) : r.dg.filter((n) => /^(GN|R1)/.test(n)), dp: [] }));
    for (const t of ts) {
      const useII5 = g2 && t.livre === 'II';
      const src = useII5 ? (t.dp5 || {}) : t.dp;
      for (const [id, nums] of Object.entries(src)) {
        let host = rows.find((r) => r.id === id);
        if (!host) {
          const r1 = A.rub1.find((r) => r.id === id);
          host = rows.find((r) => r1 && r.c === r1.c);
          if (!host && r1) { host = { c: r1.c, id: r1.id, t: r1.t, dg: [], dp: [] }; rows.push(host); }
          if (!host) host = rows[0];
        }
        host.dp = host.dp.concat(nums);
      }
    }
    if (!anyII) return rows.filter((r) => r.c === 'Classement et généralités' || r.dp.length);
    return rows;
  }
  function applAutres(codes, cat) {
    return codes.map(typeOf).filter(Boolean).flatMap((t) => ((cat === 5 && t.livre === 'II') ? (t.autres5 || []) : t.autres).map((a) => ({ s: `${t.code} · ${a.s}`, n: a.n })));
  }
  function chipHTML(num, kind, cat) {
    const n = applNode(num);
    if (!n) return `<span class="an ${kind} miss" title="Absent de la base">${esc(num)}</span>`;
    const off = cat && !artApplies(n, cat);
    return `<button class="an ${kind}${off ? ' off' : ''}" data-ref="${n.id}" title="${esc(artTitle(n))}${off ? ` (ne vise pas la ${CAT_LBL[cat]} catégorie)` : ''}">${esc(dispNum(n))}</button>`;
  }
  function textsHTML(nums, kind) {
    return nums.map((num) => {
      const n = applNode(num); if (!n) return '';
      return `<div class="atx ${kind}" data-atx="${n.id}"><div class="atx-h"><button class="an ${kind}" data-open="${n.id}" title="Lire dans le texte">${esc(dispNum(n))}</button><span>${esc(artTitle(n))}</span></div><div class="legal">${safeHTML(n.html, n.texte)}</div></div>`;
    }).join('');
  }
  function illusFor(nums) {
    const seen = new Set(); const out = [];
    for (const num of nums) for (const f of (st.illusBy && st.illusBy.get(illusKey('ERP', num))) || []) if (!seen.has(f.id)) { seen.add(f.id); out.push(f); }
    return out;
  }

  /* --- tableau d'effectif --- */
  const rid = () => Math.random().toString(36).slice(2, 9);
  const TYPE_LBL = (code) => (code === 'CT' ? 'CT' : code);
  function methOptions(code, sel) {
    const ms = st.appl.methodes.filter((m) => m.t === code);
    return ms.map((m) => `<option value="${m.id}"${m.id === sel ? ' selected' : ''}>${esc(m.ref)} : ${esc(m.o === 'niveau' ? 'selon le niveau (1/3, 1/6, 1/15 m²)' : m.lab)}</option>`).join('');
  }
  /* Types ERP du tableau, du plus fort effectif au plus faible (le premier est le type principal) */
  function rowTypes() {
    const c = calcState(); const eff = {};
    for (const r of c.rows) if (r.m && r.t !== 'CT') { const e = rowEff(r); eff[r.t] = (eff[r.t] || 0) + e.pub + e.pers + 1e-3; }
    return Object.keys(eff).sort((a, b) => eff[b] - eff[a]);
  }
  function tabsHTML(tab) {
    const T = [['eff', '1. Effectif et catégorie'], ['deg', '2. Dégagements'], ['reg', '3. Réglementation applicable']];
    return `<div class="apl-tabs" role="tablist">${T.map(([k, l]) => `<button role="tab" class="apl-tab" data-apltab="${k}" aria-selected="${tab === k}">${l}</button>`).join('')}</div>`;
  }
  function calcHTML() {
    const c = calcState();
    const all = st.appl.types.map((t) => t.code).concat(['CT']);
    const used = rowTypes();
    const order = used.concat(all.filter((x) => !used.includes(x)));
    const rows = c.rows.map((r, i) => {
      const e = rowEff(r); const m = e.m;
      return `<tr data-row="${i}" class="${m && m.o === 'noncumul' ? 'noncumul' : ''}${e.ct ? ' ctrow' : ''}">
        <td><select data-f="niv" aria-label="Niveau">${NIVEAUX.map((n) => `<option value="${n}"${+r.niv === n ? ' selected' : ''}>${nivLbl(n)}</option>`).join('')}</select></td>
        <td><input data-f="loc" value="${esc(r.loc || '')}" placeholder="Désignation du local" aria-label="Locaux"></td>
        <td><select data-f="t" aria-label="Type">${order.map((x) => `<option value="${x}"${x === r.t ? ' selected' : ''}>${x === 'CT' ? 'CT (Code du travail)' : x}</option>`).join('')}</select></td>
        <td><select data-f="m" class="msel" aria-label="Mode de calcul">${methOptions(r.t, r.m)}</select><div class="mlab" data-mlab></div></td>
        <td class="q"><input data-f="q" inputmode="decimal" value="${esc(r.q || '')}" aria-label="Quantité"><span class="u">${esc(m ? m.u : '')}</span></td>
        <td class="n"><input data-f="pub" inputmode="numeric" value="${esc(r.pub ?? '')}" placeholder="${e.calc}" aria-label="Effectif public"${e.ct ? ' disabled' : ''}></td>
        <td class="n"><input data-f="pers" inputmode="numeric" value="${esc(r.pers ?? '')}" placeholder="${e.persCalc}" aria-label="Effectif personnel"></td>
        <td class="n tot" data-tot></td>
        <td><button class="x" data-calcdel="${i}" title="Supprimer la ligne" aria-label="Supprimer la ligne">×</button></td></tr>`;
    }).join('');
    const vars = used.map(typeOf).filter((t) => t && t.var).map((t) => `<label class="cvar">${esc(t.code)} : <select data-var="${t.code}">${t.var.map((v, i) => `<option value="${i}"${(c.variants[t.code] || 0) === i ? ' selected' : ''}>${esc(v.l)}</option>`).join('')}</select></label>`).join('');
    return `<div class="calc-head"><h2>Effectif et catégorie</h2><div class="cvars">${vars}</div></div>
      <div class="ctab-wrap"><table class="ctab"><thead><tr><th>Niveau</th><th>Locaux</th><th>Type</th><th>Article et mode de calcul</th><th>Quantité</th><th>Public</th><th>Personnel</th><th>Total</th><th></th></tr></thead>
      <tbody>${rows || `<tr><td colspan="9" class="empty">Ajoutez un local : niveau, désignation, type, mode de calcul et quantité. L'effectif public se calcule ; vous pouvez le remplacer par une valeur déclarée. Type CT : locaux réservés aux travailleurs, hors classement ERP.</td></tr>`}</tbody>
      <tfoot><tr><td colspan="5">TOTAL ERP</td><td class="n" data-sum="pub"></td><td class="n" data-sum="pers"></td><td class="n" data-sum="tot"></td><td></td></tr><tr class="ctsum" data-ctsum hidden><td colspan="5">Code du travail (hors classement)</td><td class="n">—</td><td class="n" data-sum="ct"></td><td class="n" data-sum="ctt"></td><td></td></tr></tfoot></table></div>
      <div class="calc-bar"><button class="btn ghost" data-calcadd="same">+ Local au même niveau</button><button class="btn ghost" data-calcadd="up">+ Niveau au-dessus</button><button class="btn ghost" data-calcadd="down">+ Niveau en dessous</button>
        <span class="sp"></span><button class="btn ghost" data-calcclear="1">Vider</button><button class="btn ghost" data-copyprev="eff">Copier pour OpenOffice</button></div>
      <div class="calc-res" data-res></div>
      <div class="calc-go"><button class="btn" data-apltab="deg">Calculer les dégagements</button><button class="btn primary" data-generate="1">Générer la réglementation</button></div>
      <p class="hint calc-note">Arrondi à l'unité supérieure par ligne. Personnel : à compter s'il ne dispose pas de dégagements indépendants (R. 143-19, GN 1 § 2 b) ; il n'intervient pas pour la 5e catégorie. J 2 et U 2 incluent le personnel dans le calcul forfaitaire. Locaux réservés aux travailleurs avec dégagements propres : type CT, hors classement, dégagements selon le Code du travail.</p>`;
  }
  function refreshCalc() {
    const c = calcState(); const box = $('#aplPane'); if (!box || c.tab !== 'eff') return;
    let sp = 0, spe = 0, ct = 0;
    c.rows.forEach((r, i) => {
      const tr = box.querySelector(`tr[data-row="${i}"]`); if (!tr) return;
      const e = rowEff(r);
      tr.querySelector('[data-f="pub"]').placeholder = e.calc;
      tr.querySelector('[data-f="pers"]').placeholder = e.persCalc;
      tr.querySelector('[data-tot]').textContent = e.cumul ? e.pub + e.pers : `(${e.pub + e.pers})`;
      const ml = tr.querySelector('[data-mlab]'); if (ml && e.m) ml.innerHTML = `<b>${esc(e.m.ref)}</b> ${esc(methLabel(e.m, +r.niv))}`;
      if (e.ct) ct += e.pers; else if (e.cumul) { sp += e.pub; spe += e.pers; }
    });
    box.querySelector('[data-sum="pub"]').textContent = sp;
    box.querySelector('[data-sum="pers"]').textContent = spe;
    box.querySelector('[data-sum="tot"]').textContent = sp + spe;
    box.querySelector('[data-ctsum]').hidden = !ct;
    box.querySelector('[data-sum="ct"]').textContent = ct;
    box.querySelector('[data-sum="ctt"]').textContent = ct;
    const r = classer();
    const res = box.querySelector('[data-res]');
    if (!r) { res.innerHTML = '<p class="hint">La catégorie sera calculée dès qu\'une ligne ERP a un mode de calcul.</p>'; return; }
    const man = c.cat && c.cat !== r.cat;
    res.innerHTML = `<div class="cres"><span class="ccat">${CAT_LBL[r.cat]}<small>catégorie</small></span><div><b>${r.cat === 5 ? '2e groupe (livre III)' : '1er groupe (livre II)'} · type${rowTypes().length > 1 ? 's' : ''} ${esc(rowTypes().join(', '))}</b>
      <ul>${r.why.map((w) => `<li>${esc(w)}</li>`).join('')}${r.alerts.map((w) => `<li class="alert">${esc(w)}</li>`).join('')}</ul>
      ${man ? `<p class="man">Catégorie forcée à la ${CAT_LBL[c.cat]} pour l'extraction. <button class="linkish" data-calcauto="1">Revenir à la catégorie calculée</button></p>` : ''}</div></div>`;
  }
  function bindCalc() {
    const box = $('#aplPane'); if (!box) return;
    const c = calcState();
    box.oninput = (ev) => {
      if (c.tab === 'deg') { degInput(ev); return; }
      const tr = ev.target.closest('tr[data-row]'); const f = ev.target.dataset.f;
      if (!tr || !f || ev.target.tagName === 'SELECT') return;
      c.rows[+tr.dataset.row][f] = ev.target.value; saveCalc(); refreshCalc();
    };
    box.onchange = (ev) => {
      if (c.tab === 'deg') { degChange(ev); return; }
      const v = ev.target.dataset.var;
      if (v) { c.variants[v] = +ev.target.value; saveCalc(); refreshCalc(); return; }
      const tr = ev.target.closest('tr[data-row]'); const f = ev.target.dataset.f;
      if (tr && f) {
        const r = c.rows[+tr.dataset.row]; r[f] = ev.target.value;
        if (f === 't') { const m0 = st.appl.methodes.find((m) => m.t === r.t); r.m = m0 ? m0.id : ''; r.pub = ''; r.pers = ''; }
        if (f === 'm') { r.pub = ''; r.pers = ''; }
        saveCalc();
        if (f === 't' || f === 'm' || f === 'niv') renderPane();
      }
    };
  }
  function addRow(where) {
    const c = calcState(); const last = c.rows[c.rows.length - 1];
    const niv = last ? +last.niv + (where === 'up' ? 1 : where === 'down' ? -1 : 0) : 0;
    const t = last ? last.t : c.types[0];
    const m0 = (last && last.t === t && methOf(last.m)) || st.appl.methodes.find((m) => m.t === t);
    c.rows.push({ id: rid(), niv: Math.max(-3, Math.min(10, niv)), loc: '', t, m: m0 ? m0.id : '', q: '', pub: '', pers: '' });
    saveCalc(); renderPane();
    const ins = $$('#aplPane [data-f="loc"]'); if (ins.length) ins[ins.length - 1].focus();
  }
  const $$ = (s) => [...document.querySelectorAll(s)];

  /* --- dégagements --- */
  const fr = (x) => String(Math.round(x * 100) / 100).replace('.', ',');
  function upOf(e) { return e <= 100 ? 0 : Math.ceil(e / 100) + (e <= 500 ? 1 : 0); }
  function nbOf(e) { return e <= 500 ? 2 : 2 + Math.ceil((e - 500) / 500); }
  /* Exigence réglementaire : {s, u, ns, nu, mode:'up'|'w', wmin:[...], ref, note} */
  function exigence(eff, kind, groupe, ct, h8) {
    if (!eff) return null;
    if (ct) {
      const neuf = calcState().ctMode !== 'existant';
      if (neuf) {
        if (eff < 20) return { s: '1', u: '1', ns: 1, nu: 1, mode: 'up', ref: 'R. 4216-8' };
        if (eff <= 50) return { s: '1 + 1 acc.', u: '1', ns: 2, nu: 1, mode: 'up', ref: 'R. 4216-8', note: 'ou 1 dégagement de 2 UP si parcours ≤ 25 m, hors sous-sol' };
        if (eff <= 100) return { s: '2', u: '2', ns: 2, nu: 2, mode: 'up', ref: 'R. 4216-8', note: 'ou 1 + 1 accessoire' };
        return { s: String(nbOf(eff)), u: String(Math.max(3, Math.ceil(eff / 100) + (eff <= 500 ? 1 : 0))), ns: nbOf(eff), nu: Math.ceil(eff / 100) + (eff <= 500 ? 1 : 0), mode: 'up', ref: 'R. 4216-8' };
      }
      const w = eff < 20 ? 0.8 : eff <= 100 ? 1.5 : eff <= 300 ? 2 : eff <= 500 ? 2.5 : 2.5 + 0.5 * Math.ceil((eff - 500) / 100);
      const n = eff <= 100 ? 1 : eff <= 500 ? 2 : 2 + Math.ceil((eff - 500) / 500);
      return { s: String(n), u: `${fr(w)} m au total`, ns: n, nu: 0, mode: 'w', wsum: w, wmin: [0.8], ref: 'R. 4227-5' };
    }
    if (groupe === 2 && eff <= 300) {
      const esc1 = kind === 'escE';
      if (eff < 20) return { s: '1', u: '0,90 m', ns: 1, mode: 'w', alt: [[0.9]], ref: 'PE 11 § 3 a)' };
      if (eff <= 50) {
        if (esc1) return { s: h8 ? '1 + 1 acc.' : '1', u: '0,90 m', ns: h8 ? 2 : 1, mode: 'w', alt: [[0.9]], ref: 'PE 11 § 3 b)', note: h8 ? 'escalier unique complété par un accessoire (plancher > 8 m)' : 'escalier unique' };
        return { s: '1 ou 2', u: '1,40 m (sortie directe, ≤ 25 m) ou 0,90 m + 0,60 m', ns: 1, mode: 'w', alt: [[1.4], [0.9, 0.6]], ref: 'PE 11 § 3 b)' };
      }
      if (eff <= 100) return { s: '2', u: '2 × 0,90 m ou 1,40 m + 0,60 m', ns: 2, mode: 'w', alt: [[0.9, 0.9], [1.4, 0.6]], ref: 'PE 11 § 3 c)' };
      if (eff <= 200) return { s: '2', u: '1,40 m + 0,90 m', ns: 2, mode: 'w', alt: [[1.4, 0.9]], ref: 'PE 11 § 3 d)' };
      return { s: '2', u: '2 × 1,40 m', ns: 2, mode: 'w', alt: [[1.4, 1.4]], ref: 'PE 11 § 3 e)' };
    }
    const ref = groupe === 2 ? 'PE 11 § 5 et CO 38' : 'CO 38';
    if (eff < 20) return { s: '1', u: '1', ns: 1, nu: 1, mode: 'up', ref };
    if (eff <= 50) {
      if (kind === 'escE') return { s: h8 ? '1 + 1 acc.' : '1', u: '1', ns: h8 ? 2 : 1, nu: 1, mode: 'up', ref: 'CO 38 § 1 b)', note: 'escalier d\'1 UP' + (h8 ? ' complété par un accessoire (plancher > 8 m)' : '') };
      return { s: '1 + 1 acc.', u: '1 + 1 acc.', ns: 2, nu: 1, mode: 'up', ref: 'CO 38 § 1 b)' };
    }
    if (eff <= 100) return { s: '2', u: '1 UP chacune', ns: 2, nu: 2, mode: 'up', ref: 'CO 38 § 1 c)', note: 'ou 1 × 2 UP + 1 accessoire' };
    const n = nbOf(eff), u = upOf(eff);
    return { s: String(n), u: String(u), ns: n, nu: u, mode: 'up', ref: 'CO 38 § 1 d)', note: eff > 200 ? 'dégagements de 2 UP au moins (CO 36 § 3)' : '' };
  }
  function widths(txt) { return String(txt || '').split(/[+;/]|et/).map((x) => parseFloat(x.replace(',', '.').replace(/[^\d.]/g, ''))).filter((x) => x > 0).sort((a, b) => b - a); }
  function observe(ex, real) {
    if (!ex || !real || (real.s === '' && real.u === '') || real.s == null) return { t: '', k: '' };
    const ns = +real.s || 0;
    if (ex.mode === 'up') {
      const nu = +String(real.u).replace(',', '.') || 0;
      if (ns < ex.ns || nu < ex.nu) return { t: 'Insuffisant', k: 'ko' };
      if (ns === ex.ns && nu === ex.nu) return { t: 'Dimensionné', k: 'ok' };
      if (ns > ex.ns) return { t: 'En excédent', k: 'plus' };
      return { t: "En excédent d'UP", k: 'plus' };
    }
    const w = widths(real.u);
    if (ex.wsum != null) {
      const sum = w.reduce((a, b) => a + b, 0);
      if (ns < ex.ns || sum + 1e-6 < ex.wsum || w.some((x) => x < 0.8)) return { t: 'Insuffisant', k: 'ko' };
      return ns > ex.ns || sum > ex.wsum + 1e-6 ? { t: 'En excédent', k: 'plus' } : { t: 'Dimensionné', k: 'ok' };
    }
    const ok = ex.alt.some((a) => a.every((x, i) => (w[i] || 0) + 1e-6 >= x));
    if (!ok) return { t: 'Insuffisant', k: 'ko' };
    const exact = ex.alt.some((a) => a.length === w.length && a.every((x, i) => Math.abs(w[i] - x) < 1e-6));
    if (exact) return { t: 'Dimensionné', k: 'ok' };
    const need = Math.min(...ex.alt.map((a) => a.length));
    return w.length > need ? { t: 'En excédent', k: 'plus' } : { t: 'En excédent de largeur', k: 'plus' };
  }
  /* Lignes du tableau des dégagements, regroupées par niveau (du plus haut au plus bas) */
  function degModel() {
    const c = calcState();
    const cat = currentCat(); const groupe = cat === 5 ? 2 : 1;
    const h8 = !!c.h8;
    const rows = c.rows.filter((r) => r.m).map((r) => { if (!r.id) r.id = rid(); const e = rowEff(r); return { r, e, eff: e.pub + e.pers, niv: +r.niv }; });
    const nivs = [...new Set(rows.map((x) => x.niv))].sort((a, b) => b - a);
    const lvEff = {}; for (const n of nivs) lvEff[n] = rows.filter((x) => x.niv === n && x.e.cumul && !x.e.ct).reduce((k, x) => k + x.eff, 0);
    const out = [];
    for (const n of nivs) {
      const loc = rows.filter((x) => x.niv === n);
      for (const x of loc) {
        const ex = exigence(x.eff, 'local', groupe, x.e.ct, h8);
        out.push({ kind: 'loc', key: x.r.id, niv: n, loc: x.r.loc || (x.e.m ? x.e.m.lab : ''), eff: x.eff, cum: null, ex, ct: x.e.ct, nc: !x.e.cumul && !x.e.ct });
      }
      const erp = loc.filter((x) => !x.e.ct);
      if (!erp.length) continue;
      const cum = n > 0 ? nivs.filter((k) => k >= n).reduce((k, m) => k + lvEff[m], 0) : n < 0 ? nivs.filter((k) => k <= n).reduce((k, m) => k + lvEff[m], 0) : nivs.reduce((k, m) => k + lvEff[m], 0);
      let base = cum;
      const depth = parseFloat(String((c.depth || {})[n] || '').replace(',', '.')) || 0;
      let maj = '';
      if (n < 0 && depth > 2 && cum > 100) { base = Math.ceil(Math.ceil(cum / 100) * 100 * (1 + 0.1 * Math.ceil(depth - 2)) - 1e-9); maj = `effectif théorique ${base} (CO 39 § 2 : arrondi à la centaine, + 10 % par mètre au-delà de 2 m)`; }
      const kind = n > 0 ? 'escE' : n < 0 ? 'escS' : 'rdc';
      const ex = exigence(base, kind, groupe, false, h8);
      out.push({ kind: 'tot', key: 'L' + n, niv: n, loc: n === 0 ? 'Total (sorties)' : 'Total (escaliers)', eff: lvEff[n], cum: cum !== lvEff[n] ? cum : null, ex, maj });
    }
    if (nivs.length && !nivs.includes(0)) {
      const tot = nivs.reduce((k, m) => k + lvEff[m], 0);
      out.push({ kind: 'tot', key: 'ALL', niv: null, loc: 'Ensemble de l\'établissement', eff: tot, cum: null, ex: exigence(tot, 'rdc', groupe, false, h8) });
    }
    return { out, groupe, cat };
  }
  function degHTML() {
    const c = calcState(); c.deg = c.deg || {};
    const { out, groupe, cat } = degModel();
    const anyCT = out.some((x) => x.ct);
    if (!out.length) return `<div class="calc-head"><h2>Dégagements</h2></div><p class="empty">Remplissez d'abord l'onglet « Effectif et catégorie » : les dégagements se calculent local par local, puis par niveau (escaliers en étage et en sous-sol, sorties au rez-de-chaussée).</p>`;
    const anySS = out.some((x) => x.niv < 0 && x.kind === 'tot');
    let prevNiv;
    const body = out.map((x) => {
      const first = x.niv !== prevNiv; prevNiv = x.niv;
      const real = c.deg[x.key] || {};
      const ob = observe(x.ex, real);
      const wmode = x.ex && x.ex.mode === 'w';
      return `<tr class="${x.kind === 'tot' ? 'dtot' : ''}${x.ct ? ' ctrow' : ''}${x.nc ? ' noncumul' : ''}" data-dk="${x.key}">
        <td>${first || x.kind === 'tot' ? esc(x.niv == null ? '' : nivLbl(x.niv)) : ''}</td>
        <td>${esc(x.loc)}${x.ct ? ' <span class="tag">CT</span>' : ''}${x.nc ? ' <span class="tag">non cumulé</span>' : ''}${x.maj ? `<div class="mlab">${esc(x.maj)}</div>` : ''}</td>
        <td class="n">${x.eff}</td><td class="n">${x.cum == null ? '/' : x.cum}</td>
        <td class="c">${x.ex ? esc(x.ex.s) : '—'}</td><td class="c">${x.ex ? esc(x.ex.u) : '—'}${x.ex && (x.ex.note || x.ex.ref) ? `<div class="mlab">${esc([x.ex.ref, x.ex.note].filter(Boolean).join(' · '))}</div>` : ''}</td>
        <td class="c"><input data-dg="s" inputmode="numeric" value="${esc(real.s ?? '')}" aria-label="Sorties réalisées"></td>
        <td class="c"><input data-dg="u" ${wmode ? 'placeholder="1,40 + 0,90"' : 'inputmode="decimal"'} value="${esc(real.u ?? '')}" aria-label="${wmode ? 'Largeurs réalisées (m)' : 'UP réalisées'}"></td>
        <td class="c obs ${ob.k}" data-obs>${esc(ob.t)}</td></tr>`;
    }).join('');
    const nivSS = [...new Set(out.filter((x) => x.niv < 0).map((x) => x.niv))];
    return `<div class="calc-head"><h2>Dégagements</h2><span class="hint">${CAT_LBL[cat]} catégorie · ${groupe === 2 ? '5e catégorie : nombre et largeurs (PE 11)' : 'nombre et unités de passage (CO 36, CO 38)'}</span></div>
      <div class="deg-opts"><label><input type="checkbox" data-dopt="h8" ${c.h8 ? 'checked' : ''}> Plancher bas du niveau le plus haut accessible au public à plus de 8 m</label>
        ${anyCT ? `<label>Code du travail : <select data-dopt="ct"><option value="neuf"${c.ctMode !== 'existant' ? ' selected' : ''}>construction neuve (R. 4216-8)</option><option value="existant"${c.ctMode === 'existant' ? ' selected' : ''}>bâtiment existant (R. 4227-5)</option></select></label>` : ''}
        ${nivSS.map((n) => `<label>Profondeur ${nivLbl(n)} (m) <input data-depth="${n}" inputmode="decimal" value="${esc((c.depth || {})[n] || '')}" style="width:60px"></label>`).join('')}</div>
      <div class="ctab-wrap"><table class="ctab dtab"><thead>
        <tr><th rowspan="2">Niveau</th><th rowspan="2">Locaux</th><th colspan="2" class="c">Effectifs</th><th colspan="2" class="c">Réglementaires</th><th colspan="2" class="c">Réalisés</th><th rowspan="2" class="c">Observations</th></tr>
        <tr><th class="n">Niveau</th><th class="n">Cumulés</th><th class="c">Sorties</th><th class="c">${groupe === 2 ? 'Largeurs' : 'UP'}</th><th class="c">Sorties</th><th class="c">${groupe === 2 ? 'Largeurs (m)' : 'UP'}</th></tr></thead>
        <tbody>${body}</tbody></table></div>
      <div class="calc-bar"><span class="sp"></span><button class="btn ghost" data-copyprev="deg">Copier pour OpenOffice</button><button class="btn primary" data-generate="1">Générer la réglementation</button></div>
      <p class="hint calc-note">Effectif total (public + personnel sans dégagements propres). Étages : escaliers calculés sur l'effectif du niveau cumulé avec les niveaux au-dessus ; sous-sols : avec les niveaux en dessous (CO 38 § 2${groupe === 2 ? ', appliqué par analogie en 5e catégorie' : ''}). Rez-de-chaussée : sorties calculées sur l'effectif cumulé de l'établissement. Un accessoire compte comme une sortie et pas comme une UP. ${groupe === 2 ? 'Largeurs : saisissez par exemple « 1,40 + 0,90 » ; en rénovation, 0,90 m peut être ramené à 0,80 m (PE 11 § 3). Au-delà de 300 personnes, CO 38 (PE 11 § 5).' : 'Plus de 200 personnes : dégagements normaux de 2 UP au moins (CO 36 § 3).'}</p>`;
  }
  function degInput(ev) {
    const c = calcState(); c.deg = c.deg || {};
    const tr = ev.target.closest('tr[data-dk]');
    if (tr && ev.target.dataset.dg) {
      const k = tr.dataset.dk; c.deg[k] = c.deg[k] || {}; c.deg[k][ev.target.dataset.dg] = ev.target.value; saveCalc();
      const { out } = degModel(); const x = out.find((y) => y.key === k);
      const ob = observe(x && x.ex, c.deg[k]); const cell = tr.querySelector('[data-obs]');
      cell.textContent = ob.t; cell.className = 'c obs ' + ob.k;
    }
    if (ev.target.dataset.depth) { c.depth = c.depth || {}; c.depth[ev.target.dataset.depth] = ev.target.value; saveCalc(); }
  }
  function degChange(ev) {
    const c = calcState(); const o = ev.target.dataset.dopt;
    if (o === 'h8') { c.h8 = ev.target.checked; saveCalc(); renderPane(); }
    if (o === 'ct') { c.ctMode = ev.target.value; saveCalc(); renderPane(); }
    if (ev.target.dataset.depth) renderPane();
  }

  /* --- copie vers OpenOffice --- */
  const CELL = 'border:1px solid #000;padding:3px 5px;text-align:center;vertical-align:middle;font-family:Arial,Liberation Sans,sans-serif;font-size:10pt';
  const HEAD = CELL + ';font-weight:bold;font-variant:small-caps;background:#E6E6E6';
  const td = (x, o = {}) => `<td align="center" valign="middle"${o.rs ? ` rowspan="${o.rs}"` : ''}${o.cs ? ` colspan="${o.cs}"` : ''}${o.g ? ' bgcolor="#E6E6E6"' : ''} style="${o.g ? HEAD.replace('font-variant:small-caps;', '') : CELL}">${o.b ? `<b>${esc(String(x))}</b>` : esc(String(x))}</td>`;
  const th = (x, o = {}) => `<th bgcolor="#E6E6E6"${o.rs ? ` rowspan="${o.rs}"` : ''}${o.cs ? ` colspan="${o.cs}"` : ''} style="${HEAD}">${esc(x)}</th>`;
  function effTable() {
    const c = calcState(); const r = classer();
    const rows = c.rows.filter((x) => x.m).map((x) => ({ x, e: rowEff(x) })).sort((a, b) => +b.x.niv - +a.x.niv);
    if (!rows.length) return null;
    const head = `<tr>${['Niveaux', 'Locaux', 'Articles de référence', 'Mode de calcul', 'Effectif du public', 'Effectif du personnel', 'Effectif total'].map((h) => th(h)).join('')}</tr>`;
    const tsvH = 'Niveaux\tLocaux\tArticles de référence\tMode de calcul\tEffectif du public\tEffectif du personnel\tEffectif total';
    let body = ''; const tsv = []; let sp = 0, spe = 0, ct = 0;
    rows.forEach(({ x, e }, i) => {
      const m = e.m; const q = String(x.q || '').trim();
      let des = (x.loc || '').trim().replace(/«\s*/g, '« ').replace(/\s*»/g, ' »');
      if (q && m.u !== 'personnes' && !des.includes(q)) des = des ? `${des} : ${q} ${m.u}` : `${q} ${m.u}`;
      const span = rows.filter((y) => +y.x.niv === +x.niv).length;
      const first = i === 0 || +rows[i - 1].x.niv !== +x.niv;
      const tot = e.pub + e.pers;
      const totTxt = e.ct ? `${tot} (Code du travail)` : e.cumul ? String(tot) : `${tot} (non cumulé)`;
      if (e.ct) ct += tot; else if (e.cumul) { sp += e.pub; spe += e.pers; }
      body += `<tr>${first ? td(nivLbl(+x.niv), { rs: span }) : ''}${td(des)}${td(m.ref)}${td(methLabel(m, +x.niv))}${td(e.ct ? '—' : e.pub)}${td(e.pers)}${td(totTxt)}</tr>`;
      tsv.push([first ? nivLbl(+x.niv) : '', des, m.ref, methLabel(m, +x.niv), e.ct ? '—' : e.pub, e.pers, totTxt].join('\t'));
    });
    body += `<tr>${td('TOTAL', { cs: 4, g: 1, b: 1 })}${td(sp, { g: 1, b: 1 })}${td(spe, { g: 1, b: 1 })}${td(sp + spe, { g: 1, b: 1 })}</tr>`;
    tsv.push(['TOTAL', '', '', '', sp, spe, sp + spe].join('\t'));
    let after = '';
    if (r) {
      const cat = c.cat || r.cat;
      after = `Établissement de type ${rowTypes().join(', ')}, classé en ${CAT_LBL[cat]} catégorie (${cat === 5 ? 'effectif du public : ' + sp : 'effectif total : ' + (sp + spe)} personnes)${ct ? ` ; ${ct} travailleurs dans des locaux relevant du seul Code du travail` : ''}.`;
    }
    return { head, body, tsvH, tsv, after, cols: [9, 25, 11, 23, 11, 11, 10] };
  }
  function degTable() {
    const c = calcState(); c.deg = c.deg || {};
    const { out, groupe } = degModel(); if (!out.length) return null;
    const head = `<tr>${th('Niveaux', { rs: 2 })}${th('Locaux', { rs: 2 })}${th('Effectifs', { cs: 2 })}${th('Réglementaires', { cs: 2 })}${th('Réalisés', { cs: 2 })}${th('Observations', { rs: 2 })}</tr><tr>${['Niveau', 'Cumulés', 'Sorties', groupe === 2 ? 'Largeurs' : 'UP', 'Sorties', groupe === 2 ? 'Largeurs' : 'UP'].map((h) => th(h)).join('')}</tr>`;
    const tsvH = `Niveaux\tLocaux\tEffectif niveau\tEffectif cumulé\tSorties réglementaires\t${groupe === 2 ? 'Largeurs' : 'UP'} réglementaires\tSorties réalisées\t${groupe === 2 ? 'Largeurs' : 'UP'} réalisées\tObservations`;
    let body = ''; const tsv = [];
    // regroupement des locaux d'un même niveau (cellule fusionnée), ligne total à part
    for (let i = 0; i < out.length; i++) {
      const x = out[i]; const real = c.deg[x.key] || {}; const ob = observe(x.ex, real);
      const g = x.kind === 'tot';
      let nivCell = '';
      if (g) nivCell = td(x.niv == null ? '' : nivLbl(x.niv), { g: 1, b: 1 });
      else if (i === 0 || out[i - 1].niv !== x.niv || out[i - 1].kind === 'tot') {
        let span = 0; for (let j = i; j < out.length && out[j].niv === x.niv && out[j].kind === 'loc'; j++) span++;
        nivCell = td(nivLbl(x.niv), { rs: span });
      }
      const loc = x.loc + (x.ct ? ' (Code du travail)' : '') + (x.nc ? ' (non cumulé)' : '');
      const cells = [loc, x.eff, x.cum == null ? '/' : x.cum, x.ex ? x.ex.s : '—', x.ex ? x.ex.u : '—', real.s || '', real.u || '', ob.t];
      body += `<tr>${nivCell}${cells.map((v) => td(v, g ? { g: 1 } : {})).join('')}</tr>`;
      tsv.push([nivCell ? (x.niv == null ? '' : nivLbl(x.niv)) : '', ...cells].join('\t'));
    }
    return { head, body, tsvH, tsv, after: '', cols: [8, 22, 8, 8, 9, 11, 8, 9, 17] };
  }
  function tableHTML(t, lignes) {
    const cols = `<colgroup>${t.cols.map((w) => `<col width="${w}%">`).join('')}</colgroup>`;
    return `<table border="1" cellspacing="0" cellpadding="3" width="100%" style="border-collapse:collapse;width:100%">${cols}${lignes ? '' : `<thead>${t.head}</thead>`}<tbody>${t.body}</tbody></table>${!lignes && t.after ? `<p style="font-family:Arial,Liberation Sans,sans-serif;font-size:10pt;margin-top:6pt">${esc(t.after)}</p>` : ''}`;
  }
  function putClipboard(html, text) {
    const doc = `<html><head><meta charset="utf-8"></head><body>${html}</body></html>`;
    let ok = false;
    const onCopy = (ev) => { ev.clipboardData.setData('text/html', doc); ev.clipboardData.setData('text/plain', text); ev.preventDefault(); ok = true; };
    document.addEventListener('copy', onCopy);
    try { document.execCommand('copy'); } catch (e) { ok = false; }
    document.removeEventListener('copy', onCopy);
    if (ok) return Promise.resolve(true);
    if (navigator.clipboard && window.ClipboardItem) {
      return navigator.clipboard.write([new ClipboardItem({ 'text/html': new Blob([doc], { type: 'text/html' }), 'text/plain': new Blob([text], { type: 'text/plain' }) })]).then(() => true, () => false);
    }
    return Promise.resolve(false);
  }
  function copyPreview(which) {
    const t = which === 'deg' ? degTable() : effTable();
    if (!t) { toast('Le tableau est vide'); return; }
    let ov = $('#copyPrev');
    if (!ov) { ov = document.createElement('div'); ov.id = 'copyPrev'; ov.className = 'cpv'; document.body.append(ov); }
    ov.innerHTML = `<div class="cpv-box" role="dialog" aria-modal="true" aria-label="Aperçu du tableau à coller">
      <div class="cpv-head"><b>${which === 'deg' ? 'Tableau des dégagements' : "Tableau de calcul de l'effectif"}</b><button class="x" data-cpv="close" aria-label="Fermer">×</button></div>
      <p class="hint">Deux façons de coller dans OpenOffice ou LibreOffice Writer :</p>
      <div class="cpv-acts">
        <button class="btn" data-cpv="all">Copier le tableau complet</button><span class="hint">à coller sur une ligne vide : le tableau est créé avec ses en-têtes.</span>
        <button class="btn ghost" data-cpv="rows">Copier les lignes seules</button><span class="hint">à coller dans votre tableau existant, curseur dans la première cellule sous l'en-tête : les cellules sont remplies (LibreOffice 6.4 et plus).</span>
      </div>
      <p class="hint">Si le collage se fait mal, utilisez Édition › Collage spécial › Format HTML, ou sélectionnez le tableau ci-dessous à la souris et copiez-le.</p>
      <div class="cpv-doc">${tableHTML(t, false)}</div></div>`;
    ov.hidden = false;
    ov.onclick = (e) => {
      const b = e.target.closest('[data-cpv]'); if (!b && e.target !== ov) return;
      const a = b ? b.dataset.cpv : 'close';
      if (a === 'close') { ov.hidden = true; return; }
      const lignes = a === 'rows';
      const text = (lignes ? [] : [t.tsvH]).concat(t.tsv).join('\n') + (!lignes && t.after ? '\n\n' + t.after : '');
      putClipboard(tableHTML(t, lignes), text).then((ok) => toast(ok ? (lignes ? 'Lignes copiées : collez dans la première cellule de votre tableau' : 'Tableau copié : collez-le dans OpenOffice') : 'Copie impossible : sélectionnez le tableau de l\'aperçu et faites Ctrl+C'));
    };
  }

  /* --- page --- */
  function renderPane() {
    const box = $('#aplPane'); if (!box) return;
    const c = calcState();
    if (c.tab === 'deg') box.innerHTML = degHTML();
    else box.innerHTML = calcHTML();
    bindCalc(); if (c.tab === 'eff') refreshCalc();
  }
  function renderAppl() {
    setSide(false);
    const A = st.appl;
    if (!A) { $('#read').innerHTML = '<div class="home"><p class="hint">Grille indisponible (data/applicable.json).</p></div>'; return; }
    const c = calcState(); c.tab = c.tab || (c.rows.length ? 'eff' : 'reg');
    st.applOpen = st.applOpen || new Set();
    $('#read').className = 'pane readpane dom-ERP';
    const groups = [['Types (livre II)', A.types.filter((x) => x.livre === 'II')], ['Établissements spéciaux (livre IV)', A.types.filter((x) => x.livre === 'IV')]];
    const rt = rowTypes();
    const diff = rt.length && (rt.length !== c.types.length || rt.some((x) => !c.types.includes(x)));
    $('#read').innerHTML = `<div class="home appl">
      <h1>Réglementation applicable</h1>
      <p class="lead">Remplissez le tableau d'effectif niveau par niveau puis générez la réglementation : les types viennent du tableau, la catégorie est calculée. Pour aller vite, choisissez directement types et catégorie dans l'onglet 3.</p>
      ${tabsHTML(c.tab)}
      ${c.tab === 'reg' ? `<div class="apl-bar">
        <div class="apl-types" role="group" aria-label="Types de l'établissement">${groups.map(([g, ts]) => `<div class="apl-tg"><span class="lbl">${esc(g)}</span><div class="plates">${ts.map((x) => { const i = c.types.indexOf(x.code); return `<button class="tp${i === 0 ? ' princ' : ''}" data-aplt="${x.code}" aria-pressed="${i >= 0}" title="${esc(x.label)}${i === 0 ? ' (type principal)' : ''}">${esc(x.code)}</button>`; }).join('')}</div></div>`).join('')}</div>
        ${diff ? `<p class="apl-sync">Le tableau d'effectif contient les types ${esc(rt.join(', '))}. <button class="linkish" data-generate="1">Reprendre les types et la catégorie du tableau</button></p>` : ''}
      </div><section id="aplExt"></section>` : '<section class="apl-calc-box" id="aplPane"></section>'}
    </div>`;
    if (c.tab === 'reg') renderApplExt(); else renderPane();
  }
  function renderApplExt() {
    const box = $('#aplExt'); if (!box) return;
    const A = st.appl; const c = calcState();
    const cat = currentCat(); st.applShownCat = cat;
    const codes = c.types; const ts = codes.map(typeOf).filter(Boolean);
    const g2 = cat === 5 && ts.some((t) => t.livre === 'II');
    const somOffer = g2 && ts.some((t) => t.sommeil != null);
    const sommeil = somOffer && (c.sommeil != null ? c.sommeil : ts.some((t) => t.sommeil));
    const rowsAll = applRows(codes, cat, sommeil);
    const autresAll = applAutres(codes, cat);
    const f = c.filtre;
    const keep = (num) => !f || artApplies(applNode(num), cat);
    let nOff = 0;
    const rows = rowsAll.map((r) => { const dg = r.dg.filter(keep), dp = r.dp.filter(keep); nOff += r.dg.length - dg.length + r.dp.length - dp.length; return Object.assign({}, r, { dg, dp }); });
    const autres = autresAll.map((a) => { const n = a.n.filter(keep); nOff += a.n.length - n.length; return { s: a.s, n }; }).filter((a) => a.n.length);
    const calc = classer();
    const lbl = ts.map((t) => t.code).join(' + ');
    const chap5 = g2 ? ts.filter((t) => t.chap5).map((t) => t.chap5) : [];
    let regime;
    if (g2) regime = `2e groupe : livre III (PE). Les dispositions du livre II ne s'appliquent pas, sauf celles expressément citées (PE 1).${chap5.length ? ` Chapitre${chap5.length > 1 ? 's' : ''} ${[...new Set(chap5)].join(', ')} du livre III en complément.` : ''}`;
    else regime = `1er groupe : dispositions générales du livre II et dispositions particulières ${ts.length > 1 ? `de chaque type (${lbl}), appliquées selon la catégorie de l'ensemble (GN 2 § 3)` : `du type ${esc(ts[0].code)}`}.`;
    if (ts.some((t) => t.livre === 'IV')) regime += ` Les types du livre IV (${ts.filter((t) => t.livre === 'IV').map((t) => t.code).join(', ')}) ont leurs propres règles et citent eux-mêmes les articles généraux applicables.`;
    let chapN = '';
    const body = rows.map((r) => {
      const head = r.c !== chapN ? `<h2 class="apl-ch">${esc(r.c)}</h2>` : ''; chapN = r.c;
      const open = st.applOpen.has(r.id);
      const ill = illusFor(r.dg.concat(r.dp));
      return `${head}<section class="apl-row${open ? ' open' : ''}${r.dp.length ? ' has-dp' : ''}" id="apl-${r.id}">
        <div class="apl-t"><button class="apl-tog" data-apltog="${r.id}" aria-expanded="${open}"><span class="car" aria-hidden="true"></span>${esc(r.t)}</button></div>
        <div class="apl-dg">${r.dg.map((x) => chipHTML(x, 'dg', f ? 0 : cat)).join('') || '<span class="none">—</span>'}</div>
        <div class="apl-dp">${r.dp.map((x) => chipHTML(x, 'dp', f ? 0 : cat)).join('') || '<span class="none">pas de disposition particulière</span>'}</div>
        <div class="apl-il">${ill.slice(0, 3).map((x) => `<button class="apl-th" data-page="${esc(illusSrc(x))}" title="Planche : ${esc(x.titre)}"><img loading="lazy" src="${esc(illusSrc(x))}" alt=""></button>`).join('')}</div>
        ${open ? `<div class="apl-txt"><div class="col">${r.dp.length ? `<h3 class="dp">Dispositions particulières</h3>${textsHTML(r.dp, 'dp')}` : ''}</div><div class="col">${r.dg.length ? `<h3>${g2 ? 'Livre III et livre Ier' : 'Dispositions générales'}</h3>${textsHTML(r.dg, 'dg')}` : ''}</div></div>` : ''}
      </section>`;
    }).join('');
    const autresHTML = autres.length ? `<h2 class="apl-ch">Autres dispositions particulières</h2>${autres.map((a, i) => {
      const id = 'x' + i; const open = st.applOpen.has(id);
      return `<section class="apl-row${open ? ' open' : ''} has-dp" id="apl-${id}"><div class="apl-t"><button class="apl-tog" data-apltog="${id}" aria-expanded="${open}"><span class="car" aria-hidden="true"></span>${esc(a.s.replace(/(Section|Sous-section|Chapitre) [^:]*: /, ''))}</button></div>
        <div class="apl-dg"><span class="none">—</span></div><div class="apl-dp">${a.n.map((x) => chipHTML(x, 'dp', f ? 0 : cat)).join('')}</div><div class="apl-il"></div>
        ${open ? `<div class="apl-txt"><div class="col">${textsHTML(a.n, 'dp')}</div><div class="col"></div></div>` : ''}</section>`;
    }).join('')}` : '';
    const nDp = rows.reduce((k, r) => k + r.dp.length, 0) + autres.reduce((k, a) => k + a.n.length, 0);
    const nDg = rows.reduce((k, r) => k + r.dg.length, 0);
    box.innerHTML = `
      <div class="apl-card">
        <div class="apl-id"><span class="bigt">${esc(lbl)}</span><div><b>${esc(ts.map((t) => t.label).join(' · '))}</b><span>${CAT_LBL[cat]} catégorie · ${g2 ? '2e groupe' : '1er groupe'}${calc && c.cat && c.cat !== calc.cat ? ` (forcée, calculée : ${CAT_LBL[calc.cat]})` : calc ? ' (calculée)' : ''}</span></div></div>
        <div class="apl-cat"><span class="lbl">Catégorie de l'extraction</span><div class="plates" role="group" aria-label="Catégorie">${[1, 2, 3, 4, 5].map((k) => `<button class="cp" data-aplc="${k}" aria-pressed="${k === cat}">${CAT_LBL[k]}</button>`).join('')}</div>
          ${somOffer ? `<label class="apl-som"><input type="checkbox" id="aplSom" ${sommeil ? 'checked' : ''}> Locaux à sommeil (PE 28 à PE 37)</label>` : ''}</div>
        <p class="apl-reg">${regime}</p>
        <div class="apl-tools">
          <label class="apl-filt"><input type="checkbox" id="aplFilt" ${f ? 'checked' : ''}> Seulement ce qui vise la ${CAT_LBL[cat]} catégorie${f && nOff ? ` <span class="hint">(${nOff} article${nOff > 1 ? 's' : ''} écarté${nOff > 1 ? 's' : ''})</span>` : ''}</label>
          <span class="hint">${nDg} articles généraux · ${nDp} particuliers</span>
          <button class="btn ghost" id="aplAll">${st.applOpen.size ? 'Tout replier' : 'Tout déplier'}</button>
          <button class="btn ghost" id="aplCopy">Copier la liste</button>
          <button class="btn" id="aplPrint">Imprimer l'extraction</button></div>
      </div>
      <div class="apl-search"><input id="aplQ" type="search" value="${esc(st.applQ || '')}" placeholder="Rechercher dans cette réglementation : désenfumage, porte, cuisine, alarme…" aria-label="Rechercher dans la réglementation applicable"></div>
      <div id="aplRes"></div>
      <div id="aplRows"${st.applQ ? ' hidden' : ''}>
      <div class="apl-head" aria-hidden="true"><span>Rubrique</span><span>${g2 ? 'Livre III, livre Ier' : 'Dispositions générales'}</span><span>Dispositions particulières</span><span>Schémas</span></div>
      ${body}${autresHTML}</div>
      <p class="hint apl-src">${esc(A.source)}. Filtre par catégorie : un article est écarté quand son titre ou tous ses passages visent d'autres catégories ; dans les textes dépliés, les passages qui commencent par viser une autre catégorie sont masqués (cliquez pour les afficher). Les seuils d'effectif (« plus de 300 personnes ») sont surlignés pour vérification.</p>`;
    $$('#aplExt .apl-txt .legal').forEach((el) => {
      const n = st.byId.get(el.parentNode.dataset.atx);
      const tt = n && artTitle(n);
      while (el.firstElementChild && (!el.firstElementChild.textContent.trim() || el.firstElementChild.textContent.trim() === tt)) el.firstElementChild.remove();
      if (n) linkify(el, n);
      filterDom(el, cat, f);
      markCats(el, cat, calc ? calc.tot : 0);
    });
    const sb = $('#aplSom'); if (sb) sb.onchange = () => { c.sommeil = sb.checked; saveCalc(); renderApplExt(); };
    const ctx = { rows, autres, cat, f, kinds: new Map() };
    for (const r of rows) { r.dg.forEach((x) => ctx.kinds.set(x, { r: r.t, k: 'dg' })); r.dp.forEach((x) => ctx.kinds.set(x, { r: r.t, k: 'dp' })); }
    for (const a of autres) a.n.forEach((x) => ctx.kinds.set(x, { r: a.s, k: 'dp' }));
    const qi = $('#aplQ');
    qi.addEventListener('input', debounce(() => { st.applQ = qi.value; applSearch(ctx); }, 200));
    if (st.applQ) applSearch(ctx);
    $('#aplFilt').onchange = (e) => { c.filtre = e.target.checked; saveCalc(); renderApplExt(); };
    const allRows = rows.map((r) => r.id).concat(autres.map((a, i) => 'x' + i));
    $('#aplAll').onclick = () => {
      if (st.applOpen.size) st.applOpen.clear(); else allRows.forEach((id) => st.applOpen.add(id));
      const y = $('#read').scrollTop; renderApplExt(); $('#read').scrollTop = y;
    };
    $('#aplPrint').onclick = () => { allRows.forEach((id) => st.applOpen.add(id)); renderApplExt(); setTimeout(() => window.print(), 250); };
    $('#aplCopy').onclick = () => {
      const lines = [`Types ${lbl} — ${CAT_LBL[cat]} catégorie`]; let ch = '';
      for (const r of rows) { if (r.c !== ch) { lines.push('', r.c.toUpperCase()); ch = r.c; } lines.push(`${r.t} : ${r.dg.join(', ') || '—'}${r.dp.length ? ' | ' + r.dp.join(', ') : ''}`); }
      for (const a of autres) lines.push(`${a.s} : ${a.n.join(', ')}`);
      const txt = lines.join('\n');
      (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(() => toast('Liste copiée'), () => toast('Copie impossible dans ce navigateur'));
    };
  }
  /* Recherche par mot-clé limitée aux articles de l'extraction ; extraits pris dans les passages qui visent la catégorie */
  function applSearch(ctx) {
    const res = $('#aplRes'), rowsEl = $('#aplRows'); if (!res) return;
    const q = (st.applQ || '').trim();
    rowsEl.hidden = !!q;
    if (!q) { res.innerHTML = ''; return; }
    const { terms, recognized } = S.buildQuery(q, st.syn);
    const allowed = new Map();
    for (const num of ctx.kinds.keys()) { const n = applNode(num); const i = n && st.idxPos.get(n.id); if (i != null) allowed.set(i, num); }
    const sc = st.index.score(terms, (i) => allowed.has(i));
    const ids = [...allowed.keys()].filter((i) => sc[i] > 0).sort((a, b) => sc[b] - sc[a]);
    const txtOf = (n) => {
      const lines = (n.texte || '').split('\n');
      if (!ctx.f) return n.texte || '';
      const b = blocksScope(lines.slice(1), ctx.cat);
      return [lines[0]].concat(b.filter((x) => x.ok !== false).map((x) => x.t)).join('\n');
    };
    res.innerHTML = `<p class="hint apl-rescount">${ids.length ? `${ids.length} article${ids.length > 1 ? 's' : ''} de votre réglementation (${esc(ctx.rows.length ? CAT_LBL[ctx.cat] + ' catégorie' : '')}) pour « ${esc(q)} »` : `Aucun article de votre réglementation ne parle de « ${esc(q)} ».`}${recognized.length ? ' Termes associés inclus : ' + recognized.map((x) => esc(x.group.key)).join(', ') + '.' : ''}</p>
      ${ids.slice(0, 60).map((i) => {
        const n = st.idxRows[i]; const k = ctx.kinds.get(allowed.get(i));
        return `<div class="hit dom-${n.dom} apl-hit"><button class="plate an ${k.k}" data-open="${n.id}" data-ref="${n.id}">${esc(dispNum(n))}</button>
          <div><div class="where"><span class="tag ${k.k}">${k.k === 'dp' ? 'Disposition particulière' : 'Disposition générale'}</span> ${esc(k.r)} · ${esc(artTitle(n))}</div>
          <div class="snip">${S.snippet(txtOf(n), terms, 380, 2)}</div></div></div>`;
      }).join('')}`;
  }
  function applGenerate() {
    const c = calcState(); const rt = rowTypes();
    if (!rt.length) { toast("Ajoutez au moins un local d'un type ERP"); return; }
    c.types = rt; c.cat = null; c.tab = 'reg'; saveCalc(); renderAppl(); $('#read').scrollTop = 0;
  }
  function applToggleType(code) {
    const c = calcState(); const i = c.types.indexOf(code);
    if (i < 0) c.types.push(code);
    else if (c.types.length > 1) c.types.splice(i, 1);
    else { toast("Gardez au moins un type"); return; }
    saveCalc(); renderAppl();
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
      const pref = n.dom === 'DOC' ? '' : tile.prefix || (/^[A-Z]+$/.test(tile.code) ? tile.code : '');
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

  function docItemHTML(it, nc, imgs) {
    const r = pageRange(it);
    const pages = r ? Array.from({ length: Math.min(8, r[1] - r[0] + 1) }, (_, k) => r[0] + k) : [];
    return `<article class="art doc dom-DOC" id="a-${it.id}" data-art="${it.id}">
      <button class="plate" data-focus="${it.id}" aria-label="Commentaires de ${esc(dispNum(it))}">${esc(dispNum(it))}</button>
      <div class="artbody">
        <h3 class="doctitle">${esc(it.titre)}</h3>
        <div class="legal">${safeHTML(it.html, it.texte)}</div>
        ${pages.length ? `<div class="pdfpages" aria-label="Pages du document">${pages.map((p) => `<button data-page="${esc(pageImg(it, p))}" title="Agrandir la page ${p}"><img loading="lazy" src="${esc(pageImg(it, p))}" alt="Page ${p} du document"><span>p. ${p}</span></button>`).join('')}</div>` : ''}
        <div class="meta">
          ${pagesLabel(it) ? `<span class="pill">${esc(pagesLabel(it))}</span>` : ''}
          ${it.depuis ? `<span class="pill">Édition ${esc(fmtMois(it.depuis))}</span>` : ''}
          ${it.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}
        </div>
        ${imgs.length ? `<div class="thumbs" data-imgs="${it.row}"></div>` : ''}
        <div class="acts">
          <button data-focus="${it.id}" data-tab="cmt">💬 ${nc ? nc + ' commentaire' + (nc > 1 ? 's' : '') : 'Commenter'}${nc ? `<span class="stack">${[...new Map((st.cmtBy.get(it.row) || []).map((c) => [authorName(c), c])).values()].slice(0, 4).map((c) => avatar(agentOf(c), c.auteur, 20)).join('')}</span>` : ''}</button>
          <button data-pin="${it.id}">📌 Épingler</button>
          <button data-copy="${it.id}">Copier la référence</button>
          ${it.lien ? `<a class="ss" href="${esc(it.lien)}" target="_blank" rel="noopener">PDF ${esc(pagesLabel(it))} ↗</a>` : ''}
        </div>
      </div></article>`;
  }

  function itemHTML(it) {
    if (it.type !== 'Article') {
      const rel = it.niveau - readCtx.root.niveau;
      return `<div class="sechead${rel <= 1 ? ' l1' : ''}" id="s-${it.id}">${rel <= 1 ? `<h2>${esc(it.titre)}</h2>` : `<h3>${esc(it.titre)}</h3>`}</div>`;
    }
    const nc = (st.cmtBy.get(it.row) || []).length;
    const imgs = (st.cmtBy.get(it.row) || []).flatMap((c) => c.images).slice(0, 6);
    const recent = it.depuis && it.depuis >= new Date(Date.now() - 365 * 864e5).toISOString().slice(0, 10);
    if (it.dom === 'DOC') return docItemHTML(it, nc, imgs);
    const cites = st.citedBy.get(it.id) || [];
    return `<article class="art dom-${it.dom}${it.etat === 'A_VENIR' ? ' abroge' : ''}" id="a-${it.id}" data-art="${it.id}">
      <button class="plate" data-focus="${it.id}" aria-label="Commentaires et historique de ${esc(dispNum(it))}">${esc(dispNum(it))}${it.etat === 'A_VENIR' ? '<small>à venir</small>' : ''}</button>
      <div class="artbody">
        ${cites.length ? `<div class="cited top"><span>Commenté dans</span>${cites.slice(0, 6).map((c) => `<button class="docref dom-DOC" data-open="${c.id}" title="${esc(c.titre)}">${esc(dispNum(c))}<em>${esc(c.titre)}</em></button>`).join('')}${cites.length > 6 ? `<span class="hint">+${cites.length - 6}</span>` : ''}</div>` : ''}
        ${it.etat === 'A_VENIR' ? `<p class="pill warn">Entre en vigueur le ${fmtDate(it.futDate)}</p>` : `<div class="legal">${safeHTML(it.html, it.texte)}</div>`}
        ${it.nota ? `<div class="nota"><b>Nota :</b> ${esc(it.nota)}</div>` : ''}
        ${figHTML(it)}
        ${it.fut ? `<details class="future"${it.etat === 'A_VENIR' ? ' open' : ''}><summary><b>Nouvelle rédaction au ${fmtDate(it.futDate)}</b> — voir les changements</summary><div class="legal diff" data-diff="${it.id}"></div></details>` : ''}
        <div class="meta">
          ${it.depuis ? `<span class="pill${recent ? ' new' : ''}">En vigueur depuis le ${fmtDate(it.depuis)}</span>` : ''}
          ${it.futDate && it.etat !== 'A_VENIR' ? `<span class="pill warn">Modifié au ${fmtDate(it.futDate)}</span>` : ''}
          ${it.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join('')}
        </div>
        ${imgs.length ? `<div class="thumbs" data-imgs="${it.row}"></div>` : ''}
        <div class="acts">
          <button data-focus="${it.id}" data-tab="cmt">💬 ${nc ? nc + ' commentaire' + (nc > 1 ? 's' : '') : 'Commenter'}${nc ? `<span class="stack">${[...new Map((st.cmtBy.get(it.row) || []).map((c) => [authorName(c), c])).values()].slice(0, 4).map((c) => avatar(agentOf(c), c.auteur, 20)).join('')}</span>` : ''}</button>
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
        ${illusCardHTML(n)}
        ${cm.length ? cm.map((c) => `<div class="cmt">${avatar(agentOf(c), c.auteur, 36)}<div class="cbody"><div class="cname">${esc(authorName(c))}</div>
          <div class="who">${c.type ? `<span class="pill">${esc(c.type)}</span>` : ''}<span>${fmtDate(c.date)}</span></div>
          ${c.texte ? `<div class="txt">${esc(c.texte)}</div>` : ''}${c.images.length ? `<div class="thumbs" data-cimgs="${c.row}"></div>` : ''}</div></div>`).join('') : (illusOf(n).length ? '' : '<p class="hint" style="margin-top:10px">Pas encore de commentaire sur cet article.</p>')}
        <form class="form" id="cform">
          ${st.me ? `<div class="asme">${avatar(st.me, '', 28)}<span>Publier en tant que <b>${esc(agentName(st.me))}</b></span></div>` : ''}
          <select name="type" aria-label="Type de commentaire">${['Interprétation', 'Retour terrain', 'Photo / schéma', 'Question', 'Jurisprudence', 'Doctrine / réponse ministérielle'].map((t) => `<option>${t}</option>`).join('')}</select>
          <textarea name="texte" placeholder="Votre interprétation, un retour de visite, une question…" aria-label="Commentaire"></textarea>
          <label class="drop" id="drop">Glissez des photos ou schémas ici, ou <u>choisissez des fichiers</u><input type="file" name="files" accept="image/*" multiple hidden></label>
          <div class="thumbs" id="preview"></div>
          <button class="btn" type="submit">Publier le commentaire</button>
        </form>`;
    } else if (st.sideTab === 'hist' && n.dom === 'DOC') {
      const d = st.byId.get(n.legitext) || {};
      body = `<ul class="hist"><li><b>${esc(d.titre || '')}</b></li>${d.nota ? `<li>Source : ${esc(d.nota)}</li>` : ''}${d.depuis ? `<li>Édition ${esc(fmtMois(d.depuis))}</li>` : ''}<li>Fiche §${esc(n.num)}, ${esc(pagesLabel(n))}</li></ul>
        <p style="margin-top:14px">${n.lien ? `<a href="${esc(n.lien)}" target="_blank" rel="noopener">Ouvrir le PDF à cette page ↗</a>` : ''}</p>`;
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
        const rec = { Article: n.row, Type: f.type.value, Texte: texte };
        if (files.length) {
          if (st.inGrist) { await ensureCol('REG_Commentaires', 'Images_data'); rec.Images_data = JSON.stringify(await Promise.all(files.map((x) => toDataURL(x)))); }
          else rec.Images = ['L', ...(await upload(files))];
        }
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
    const m = q.trim().match(/^(?:type\s+)?([a-z]{1,3}|[A-Z]{4,6})$/i); if (!m) return null;
    if (m[1].length > 3 && m[1] !== m[1].toUpperCase()) return null; // « bois » reste une recherche, « BOIS » ouvre le document
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
      <div><div class="where">${esc(DOMAINES[n.dom].court)} › ${esc(n.chemin.split(' › ').slice(-2).join(' › '))}${n.dom === 'DOC' && n.type === 'Article' ? ` › <b>${esc(n.titre)}</b>` : ''}</div>
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
      ${shown.slice(0, 6).map((i) => hitHTML(st.idxRows[i], r.terms)).join('')}
      ${jurisHitsHTML(q, r.terms, 3)}
      ${shown.slice(6).map((i) => hitHTML(st.idxRows[i], r.terms)).join('')}
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
      ${jurisHitsHTML(q, r.terms, 3)}
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
    const natures = ['Modification', 'Nouvel article', 'Abrogation', 'Modification à venir', 'Parution SiteSecurite', 'Nouveau document', 'Document mis à jour'];
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
    if (d.page) { const lb = $('#lightbox'); $('img', lb).src = d.page; lb.classList.add('show'); return; }
    if (d.board) { go({ v: 'board', dom: d.board }); return; }
    if (d.planches) { go({ v: 'planches' }); return; }
    if (d.appl) { go({ v: 'appl' }); return; }
    if (d.juris) { go({ v: 'juris' }); return; }
    if (d.jfocus != null) { go({ v: 'juris', q: d.jq || '', focus: +d.jfocus }); return; }
    if (d.jall != null) { go({ v: 'juris', q: d.jall }); return; }
    if (d.jsec != null) { st.view.sec = d.jsec; renderJuris(st.view.q, d.jsec); return; }
    if (d.addschema) { addSchemaForm(d.addschema === '1' ? '' : d.addschema); return; }
    if (d.aplt) { applToggleType(d.aplt); return; }
    if (d.aplc) { const c = calcState(); const r = classer(); c.cat = r && r.cat === +d.aplc ? null : +d.aplc; saveCalc(); renderApplExt(); return; }
    if (d.calcauto) { calcState().cat = null; saveCalc(); renderPane(); return; }
    if (d.apltab) { const c = calcState(); c.tab = d.apltab; saveCalc(); renderAppl(); return; }
    if (d.generate) { applGenerate(); return; }
    if (d.copyprev) { copyPreview(d.copyprev); return; }
    if (d.calcadd) { addRow(d.calcadd); return; }
    if (d.calcdel != null) { const c = calcState(); c.rows.splice(+d.calcdel, 1); saveCalc(); renderPane(); return; }
    if (d.calcclear) { const c = calcState(); if (c.rows.length && t.dataset.armed !== '1') { t.dataset.armed = '1'; t.textContent = 'Confirmer : vider le tableau'; return; } c.rows = []; c.cat = null; c.deg = {}; saveCalc(); renderPane(); return; }
    if (d.apltog) { const y = $('#read').scrollTop; st.applOpen.has(d.apltog) ? st.applOpen.delete(d.apltog) : st.applOpen.add(d.apltog); renderApplExt(); $('#read').scrollTop = y; return; }
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
    if (d.copy) { const n = st.byId.get(d.copy); const ref = n.dom === 'DOC' ? `${n.chemin.split(' › ')[0]}, §${n.num} ${n.titre} (${pagesLabel(n)})` : `${dispNum(n)} — ${n.chemin.split(' › ')[0]}`; try { await navigator.clipboard.writeText(ref); toast('Référence copiée'); } catch (err) { toast(ref); } return; }
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
  $('#btnAppl').onclick = () => go({ v: 'appl' });
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
    await loadUserIllus(data.sch);
    buildPlans();
    if (keep) st.active = st.byId.get(keep);
    updateBadge(); renderChips();
    if (st.view && st.view.v === 'read' && st.active) { renderSide(); refreshArticle(st.active); } else if (st.view && st.view.v === 'veille') renderVeille();
    else if (st.view && st.view.v === 'planches') renderPlanches(st.view.q);
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
    if (!st.illus) loadIllus(await fetch('illustrations/index.json', { cache: 'no-cache' }).then((r) => r.json()).catch(() => null));
    if (!st.appl) st.appl = await fetch('data/applicable.json', { cache: 'no-cache' }).then((r) => r.json()).catch(() => null);
    if (!st.juris) st.juris = await fetch('data/jurisprudence.json', { cache: 'no-cache' }).then((r) => r.json()).catch(() => null);
    jurisIndex();
    const data = await fetchAll();
    ingest(data);
    await loadUserIllus(data.sch);
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
