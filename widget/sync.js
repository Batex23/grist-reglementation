/* Installation des tables REG_ et mise à jour de la réglementation depuis les données publiées
   à côté du widget (data/). Tout passe par les droits de l'agent connecté : aucune clé API. */
(function (global) {
  'use strict';

  const ch = (...v) => JSON.stringify({ choices: v });
  const DOMS = ['ERP', 'IGH', 'HAB', 'CDT', 'CCH'];

  // [id, type, widgetOptions?, formule déclencheur?]
  const SCHEMA = {
    REG_Articles: [
      ['Identifiant', 'Text'], ['Parent', 'Text'], ['Type', 'Choice', ch('Texte', 'Section', 'Article')],
      ['Domaine', 'Choice', ch(...DOMS)], ['Numero', 'Text'], ['Titre', 'Text'], ['Chemin', 'Text'],
      ['Niveau', 'Int'], ['Ordre', 'Int'], ['Texte', 'Text'], ['Texte_HTML', 'Text'], ['Nota', 'Text'],
      ['Etat', 'Choice', ch('VIGUEUR', 'VIGUEUR_DIFF', 'MODIFIE', 'A_VENIR', 'ABROGE')],
      ['En_vigueur_depuis', 'Date'], ['Fin_de_vigueur', 'Date'], ['Historique', 'Text'],
      ['Version_a_venir', 'Text'], ['Version_a_venir_HTML', 'Text'], ['Date_a_venir', 'Date'], ['A_venir_par', 'Text'],
      ['Texte_officiel', 'Text'], ['Derniere_modif_texte', 'Date'], ['Lien_Legifrance', 'Text'],
      ['Mots_cles', 'ChoiceList', ch()], ['Vecteur', 'Text'], ['Mis_a_jour', 'Date'],
    ],
    REG_Commentaires: [
      ['Article', 'Ref:REG_Articles'],
      ['Type', 'Choice', ch('Interprétation', 'Retour terrain', 'Photo / schéma', 'Question', 'Jurisprudence', 'Doctrine / réponse ministérielle')],
      ['Texte', 'Text'], ['Images', 'Attachments'],
      ['Auteur', 'Text', null, 'user.Name'], ['Auteur_email', 'Text', null, 'user.Email'],
      ['Cree_le', 'DateTime:Europe/Paris', null, 'NOW()'],
    ],
    REG_Veille: [
      ['Date', 'Date'], ['Domaine', 'Choice', ch(...DOMS, 'Divers')],
      ['Nature', 'Choice', ch('Modification', 'Nouvel article', 'Abrogation', 'Modification à venir', 'Parution SiteSecurite')],
      ['Titre', 'Text'], ['Article', 'Ref:REG_Articles'], ['Ancien_texte', 'Text'], ['Nouveau_texte', 'Text'],
      ['Source', 'Text'], ['Lien', 'Text'], ['Date_effet', 'Date'],
      ['Statut', 'Choice', ch('À lire', 'Lu', 'Impact analysé')], ['Analyse', 'Text'], ['Cle', 'Text'],
    ],
    REG_Synonymes: [['Terme', 'Text'], ['Equivalents', 'Text']],
    REG_Parametres: [['Cle', 'Text'], ['Valeur', 'Text']],
  };
  const DATE_COLS = new Set(['En_vigueur_depuis', 'Fin_de_vigueur', 'Date_a_venir', 'Derniere_modif_texte', 'Mis_a_jour', 'Date', 'Date_effet']);
  const SYNC_FIELDS = ['Identifiant', 'Parent', 'Type', 'Domaine', 'Numero', 'Titre', 'Chemin', 'Niveau', 'Ordre', 'Texte', 'Texte_HTML',
    'Nota', 'Etat', 'En_vigueur_depuis', 'Fin_de_vigueur', 'Historique', 'Version_a_venir', 'Version_a_venir_HTML', 'Date_a_venir',
    'A_venir_par', 'Texte_officiel', 'Derniere_modif_texte', 'Lien_Legifrance', 'Vecteur'];
  const COMPARE = ['Texte', 'Etat', 'Version_a_venir', 'Titre', 'Chemin', 'Ordre', 'Parent', 'Vecteur', 'Texte_HTML', 'Historique'];

  const ts = (iso) => { if (!iso) return null; const [y, m, d] = iso.slice(0, 10).split('-').map(Number); return Date.UTC(y, m - 1, d) / 1000; };
  const iso = (v) => (v == null || v === '' ? '' : typeof v === 'number' ? new Date(v * 1000).toISOString().slice(0, 10) : String(v).slice(0, 10));
  const today = () => new Date().toISOString().slice(0, 10);
  const frDate = (s) => (s ? new Date(s + 'T12:00:00').toLocaleDateString('fr-FR') : '');
  const parse = (s) => { try { return s ? JSON.parse(s) : []; } catch (e) { return []; } };
  const val = (f, k) => (DATE_COLS.has(k) ? iso(f[k]) : (f[k] == null ? '' : f[k]));

  function rowsOf(t) {
    const keys = Object.keys(t); const n = (t.id || []).length; const out = [];
    for (let i = 0; i < n; i++) { const r = {}; for (const k of keys) r[k] = t[k][i]; out.push(r); }
    return out;
  }

  /* ---------- adaptateurs ---------- */
  const GristAdapter = {
    async tables() {
      if (grist.docApi.listTables) return new Set(await grist.docApi.listTables());
      const t = await grist.docApi.fetchTable('_grist_Tables');
      return new Set(t.tableId);
    },
    async fetch(name) { return rowsOf(await grist.docApi.fetchTable(name)); },
    async apply(actions) { return grist.docApi.applyUserActions(actions); },
  };

  /* Document en mémoire : démonstration hors Grist et tests */
  function MemoryAdapter() {
    const T = {}; let next = 1;
    const A = {
      T,
      async tables() { return new Set(Object.keys(T)); },
      async fetch(name) {
        if (!T[name]) throw new Error('table inconnue ' + name);
        return T[name].map((r) => ({ ...r }));
      },
      async apply(actions) {
        const ret = [];
        for (const a of actions) {
          const [op, tb] = a;
          if (op === 'AddTable') { T[tb] = []; ret.push(null); } else if (op === 'ModifyColumn') ret.push(null);
          else if (op === 'AddRecord') { const id = next++; const r = { id, ...a[3] }; if (tb === 'REG_Commentaires') { r.Auteur = r.Auteur || 'Vous'; r.Cree_le = r.Cree_le || Date.now() / 1000; } T[tb].push(r); ret.push(id); }
          else if (op === 'BulkAddRecord') { const ids = []; const cols = a[3]; a[2].forEach((_, i) => { const id = next++; const r = { id }; for (const k in cols) r[k] = cols[k][i]; T[tb].push(r); ids.push(id); }); ret.push(ids); }
          else if (op === 'UpdateRecord') { Object.assign(T[tb].find((r) => r.id === a[2]), a[3]); ret.push(null); }
          else if (op === 'BulkUpdateRecord') { const cols = a[3]; a[2].forEach((id, i) => { const r = T[tb].find((x) => x.id === id); for (const k in cols) r[k] = cols[k][i]; }); ret.push(null); }
          else throw new Error('action non gérée ' + op);
        }
        return { retValues: ret };
      },
    };
    return A;
  }

  /* ---------- installation ---------- */
  async function missingTables(ad) {
    const have = await ad.tables();
    return Object.keys(SCHEMA).filter((t) => !have.has(t));
  }

  async function install(ad, synonyms) {
    const miss = await missingTables(ad);
    // les tables référencées d'abord
    miss.sort((a, b) => (a === 'REG_Articles' ? -1 : b === 'REG_Articles' ? 1 : 0));
    for (const t of miss) {
      const cols = SCHEMA[t];
      await ad.apply([['AddTable', t, cols.map(([id, type]) => ({ id, type, isFormula: false }))]]);
      const mods = [];
      for (const [id, , opts, trig] of cols) {
        if (opts) mods.push(['ModifyColumn', t, id, { widgetOptions: opts }]);
        if (trig) mods.push(['ModifyColumn', t, id, { formula: trig, isFormula: false, recalcWhen: 0, recalcDeps: null }]);
      }
      if (mods.length) await ad.apply(mods);
    }
    if (miss.includes('REG_Synonymes') && synonyms) {
      const keys = Object.keys(synonyms);
      await ad.apply([['BulkAddRecord', 'REG_Synonymes', keys.map(() => null), { Terme: keys, Equivalents: keys.map((k) => synonyms[k]) }]]);
    }
    return miss;
  }

  /* ---------- paramètres ---------- */
  async function getParam(ad, cle) {
    const r = (await ad.fetch('REG_Parametres')).find((x) => x.Cle === cle);
    return r ? r.Valeur : null;
  }
  async function setParam(ad, cle, valeur) {
    const r = (await ad.fetch('REG_Parametres')).find((x) => x.Cle === cle);
    if (r) await ad.apply([['UpdateRecord', 'REG_Parametres', r.id, { Valeur: valeur }]]);
    else await ad.apply([['AddRecord', 'REG_Parametres', null, { Cle: cle, Valeur: valeur }]]);
  }

  /* ---------- écriture par lots ---------- */
  function toCols(rows, keys) {
    const cols = {}; for (const k of keys) cols[k] = rows.map((r) => (k in r ? r[k] : null));
    return cols;
  }
  async function bulkAdd(ad, table, rows, onStep) {
    const ids = [];
    for (let i = 0; i < rows.length; i += 150) {
      const part = rows.slice(i, i + 150);
      const keys = [...new Set(part.flatMap(Object.keys))];
      const r = await ad.apply([['BulkAddRecord', table, part.map(() => null), toCols(part, keys)]]);
      ids.push(...r.retValues[0]);
      onStep && onStep(part.length);
    }
    return ids;
  }
  async function bulkUpdate(ad, table, upd, onStep) {
    // regroupe par jeu de colonnes identique
    const groups = new Map();
    for (const u of upd) { const k = Object.keys(u.fields).sort().join(','); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(u); }
    for (const [k, list] of groups) {
      const keys = k.split(',');
      for (let i = 0; i < list.length; i += 150) {
        const part = list.slice(i, i + 150);
        await ad.apply([['BulkUpdateRecord', table, part.map((u) => u.id), toCols(part.map((u) => u.fields), keys)]]);
        onStep && onStep(part.length);
      }
    }
  }

  function record(n, day) {
    const f = {};
    for (const k of SYNC_FIELDS) f[k] = DATE_COLS.has(k) ? ts(n[k]) : (n[k] == null ? (k === 'Niveau' || k === 'Ordre' ? 0 : '') : n[k]);
    f.Mis_a_jour = ts(day);
    return f;
  }

  /* ---------- comparaison et veille (même logique que sync/grist_sync.py) ---------- */
  async function apply(ad, nouveaux, actus, onProgress) {
    const day = today();
    const existRows = await ad.fetch('REG_Articles');
    const exist = new Map(existRows.filter((r) => r.Identifiant).map((r) => [r.Identifiant, r]));
    const parNum = new Map();
    for (const r of exist.values()) if (r.Type === 'Article' && r.Etat !== 'ABROGE') parNum.set(r.Texte_officiel + '|' + r.Numero, r);
    const nouveauxIds = new Set(nouveaux.map((n) => n.Identifiant));
    const deja = new Set((await ad.fetch('REG_Veille')).map((r) => r.Cle));
    const initial = exist.size === 0;
    const veille = [], maj = new Map(), ajout = [];
    const note = (v) => { if (deja.has(v.Cle)) return; deja.add(v.Cle); veille.push({ Statut: 'À lire', Date: ts(day), ...v }); };

    for (const n of nouveaux) {
      const f = record(n, day);
      let r = exist.get(n.Identifiant);
      if (!r && n.Type === 'Article') {
        const ancien = parNum.get(n.Texte_officiel + '|' + n.Numero);
        if (ancien && !nouveauxIds.has(ancien.Identifiant)) {
          maj.set(ancien.id, f); // même ligne : commentaires et mots-clés conservés
          exist.set(n.Identifiant, ancien);
          if ((ancien.Texte || '') !== (n.Texte || '')) {
            const h = parse(n.Historique);
            note({ Domaine: n.Domaine, Nature: 'Modification', Titre: `Article ${n.Numero} modifié`, Article: ancien.id,
              Ancien_texte: ancien.Texte, Nouveau_texte: n.Texte, Source: h.length ? h[h.length - 1].texte : '',
              Lien: n.Lien_Legifrance, Date_effet: ts(n.En_vigueur_depuis), Cle: `modif:${n.Identifiant}` });
          }
          continue;
        }
      }
      if (!r) { ajout.push(f); continue; }
      const changed = COMPARE.some((k) => String(val(r, k)) !== String(n[k] == null ? '' : n[k]));
      if (changed) maj.set(r.id, f);
      if (!initial && n.Type === 'Article' && r.Texte && (r.Texte || '') !== (n.Texte || '')) {
        note({ Domaine: n.Domaine, Nature: 'Modification', Titre: `Article ${n.Numero} modifié`, Article: r.id,
          Ancien_texte: r.Texte, Nouveau_texte: n.Texte, Lien: n.Lien_Legifrance, Date_effet: ts(n.En_vigueur_depuis),
          Cle: `modif:${n.Identifiant}:${n.En_vigueur_depuis}` });
      }
    }
    for (const [ident, r] of exist) {
      if (nouveauxIds.has(ident) || r.Type !== 'Article' || r.Etat === 'ABROGE' || maj.has(r.id)) continue;
      maj.set(r.id, { Etat: 'ABROGE', Fin_de_vigueur: ts(day), Mis_a_jour: ts(day) });
      note({ Domaine: r.Domaine, Nature: 'Abrogation', Titre: `Article ${r.Numero} abrogé`, Article: r.id,
        Ancien_texte: r.Texte, Lien: r.Lien_Legifrance, Cle: `abro:${ident}` });
    }

    const total = maj.size + ajout.length; let done = 0;
    const step = (k) => { done += k; onProgress && onProgress(done, total); };
    // les lignes abrogées ont moins de colonnes : regroupement fait par bulkUpdate
    await bulkUpdate(ad, 'REG_Articles', [...maj].map(([id, fields]) => ({ id, fields })), step);
    const ids = ajout.length ? await bulkAdd(ad, 'REG_Articles', ajout, step) : [];
    const rows = new Map([...exist].map(([k, r]) => [k, r.id]));
    ajout.forEach((f, i) => rows.set(f.Identifiant, ids[i]));
    if (!initial) {
      ajout.forEach((f, i) => {
        if (f.Type === 'Article' && f.Etat !== 'A_VENIR') {
          note({ Domaine: f.Domaine, Nature: 'Nouvel article', Titre: `Nouvel article ${f.Numero}`, Article: ids[i],
            Nouveau_texte: f.Texte, Lien: f.Lien_Legifrance, Date_effet: f.En_vigueur_depuis, Cle: `nouv:${f.Identifiant}` });
        }
      });
    }
    for (const n of nouveaux) {
      if (n.Type !== 'Article' || !n.Version_a_venir) continue;
      const h = parse(n.A_venir_par);
      const nouveau = n.Etat === 'A_VENIR';
      note({ Domaine: n.Domaine, Nature: 'Modification à venir',
        Titre: `${nouveau ? 'Nouvel article' : 'Article'} ${n.Numero} : ${nouveau ? 'entre en vigueur' : 'nouvelle rédaction'} le ${frDate(n.Date_a_venir)}`,
        Article: rows.get(n.Identifiant) || null, Ancien_texte: n.Texte, Nouveau_texte: n.Version_a_venir,
        Source: h.length ? h[h.length - 1].texte : '', Lien: n.Lien_Legifrance, Date_effet: ts(n.Date_a_venir),
        Cle: `avenir:${n.Numero}:${n.Texte_officiel}:${n.Date_a_venir}` });
    }
    for (const a of actus || []) {
      note({ Domaine: a.Domaine, Nature: 'Parution SiteSecurite', Titre: a.Titre, Source: a.Source, Lien: a.Lien,
        Date: ts(a.Date) || ts(day), Cle: a.Cle });
    }
    if (veille.length) await bulkAdd(ad, 'REG_Veille', veille);
    return { ajout: ajout.length, maj: maj.size, veille: veille.length };
  }

  /* ---------- point d'entrée ---------- */
  async function getJSON(path) {
    const r = await fetch(path, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`${path} : ${r.status}`);
    return r.json();
  }

  /* Vérifie la version publiée et met le document à jour si besoin.
     Renvoie {etat: 'a_jour' | 'maj' | 'occupe' | 'lecture_seule', version, resultat} */
  async function update(ad, { onProgress, force } = {}) {
    const v = await getJSON('data/version.json');
    const locale = await getParam(ad, 'version_donnees');
    if (!force && locale === v.version) return { etat: 'a_jour', version: v };
    // verrou simple : un seul agent applique la mise à jour à la fois
    const verrou = await getParam(ad, 'maj_en_cours');
    if (!force && verrou && Date.now() - Number(verrou) < 5 * 60e3) return { etat: 'occupe', version: v };
    try { await setParam(ad, 'maj_en_cours', String(Date.now())); } catch (e) { return { etat: 'lecture_seule', version: v }; }
    try {
      const [regl, actus] = await Promise.all([getJSON('data/reglementation.json'), getJSON('data/actus.json').catch(() => [])]);
      const resultat = await apply(ad, regl, actus, onProgress);
      await setParam(ad, 'version_donnees', v.version);
      await setParam(ad, 'base_legifrance', v.base || '');
      return { etat: 'maj', version: v, resultat };
    } finally {
      await setParam(ad, 'maj_en_cours', '').catch(() => {});
    }
  }

  global.RegSync = { SCHEMA, GristAdapter, MemoryAdapter, missingTables, install, update, apply, getParam };
})(window);
