/* Moteur de recherche local : mots-clés (BM25 + racinisation française + synonymes métier)
   et recherche sémantique optionnelle (modèle e5 exécuté dans le navigateur). */
(function (global) {
  'use strict';

  const STOP = new Set(('a au aux avec ce ces dans de des du elle en et eux il je la le les leur lui ma mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous c d j l m n s t y ete etre est sont etait ont a ai avez avons cette cet celui celle ceux celles dont ou si ni plus moins tout tous toute toutes autre autres doit doivent peut peuvent sous entre lorsque lors quand comme ainsi afin ils elles leurs quel quelle quels quelles faut il-y combien comment pourquoi quoi est-ce faire fait sont-ils dois-je mon ma mes notre nos chez avoir y-a-t-il').split(/\s+/));

  function fold(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, ' ').replace(/œ/g, 'oe');
  }

  function stem(w) {
    if (w.length <= 3 || /\d/.test(w)) return w;
    const suf = ['issements', 'issement', 'atrices', 'ateurs', 'ations', 'atrice', 'ateur', 'ation', 'ements', 'ement',
      'ances', 'ences', 'ance', 'ence', 'ismes', 'isme', 'istes', 'iste', 'ables', 'able', 'ibles', 'ible', 'iques', 'ique',
      'euses', 'euse', 'eurs', 'eur', 'ites', 'ite', 'ives', 'ive', 'ifs', 'if', 'elles', 'elle', 'ees', 'ee', 'es', 'er', 'ez', 'e', 's', 'x'];
    for (const s of suf) {
      if (w.endsWith(s) && w.length - s.length >= 4) return w.slice(0, -s.length);
    }
    return w;
  }

  function tokens(s) {
    return fold(s).split(/[^a-z0-9]+/).filter((t) => t && !STOP.has(t));
  }
  function terms(s) { return tokens(s).map(stem); }

  /* Numéro normalisé : « CO 15 » → CO15 ; « R. 4227-28 » → R4227-28 */
  function normNum(s) { return (s || '').toUpperCase().replace(/ARTICLES?/g, '').replace(/[\s.*]/g, ''); }

  class Index {
    constructor(docs) {
      // docs : [{key, fields:{num, path, body, extra}}]
      this.docs = docs;
      this.post = new Map();
      this.len = new Float32Array(docs.length);
      const W = { num: 4, path: 1.3, body: 1, extra: 1.6 };
      let total = 0;
      docs.forEach((d, i) => {
        const tf = new Map();
        let L = 0;
        for (const f in W) {
          const ts = terms(d.fields[f] || '');
          L += ts.length;
          for (const t of ts) tf.set(t, (tf.get(t) || 0) + W[f]);
        }
        this.len[i] = L; total += L;
        for (const [t, v] of tf) {
          let p = this.post.get(t);
          if (!p) this.post.set(t, (p = []));
          p.push(i, v);
        }
      });
      this.avg = total / Math.max(1, docs.length);
      this.N = docs.length;
    }
    score(qterms, filter) {
      // qterms : Map terme → poids
      const k1 = 1.3, b = 0.72;
      const sc = new Float32Array(this.N);
      for (const [t, w] of qterms) {
        const p = this.post.get(t);
        if (!p) continue;
        const df = p.length / 2;
        const idf = Math.log(1 + (this.N - df + 0.5) / (df + 0.5));
        for (let j = 0; j < p.length; j += 2) {
          const i = p[j], tf = p[j + 1];
          if (filter && !filter(i)) continue;
          sc[i] += w * idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * this.len[i] / this.avg));
        }
      }
      return sc;
    }
  }

  class Synonyms {
    constructor(rows) {
      this.groups = rows.map((r) => {
        const all = [r.Terme, ...(r.Equivalents || '').split(',')].map((x) => x.trim()).filter(Boolean);
        return { key: r.Terme, phrases: all.map((p) => ({ raw: p, f: fold(p).trim(), t: terms(p) })) };
      });
    }
    /* renvoie les groupes reconnus dans la requête */
    match(q) {
      const fq = ' ' + fold(q).replace(/[^a-z0-9]+/g, ' ') + ' ';
      const hits = [];
      for (const g of this.groups) {
        for (const p of g.phrases) {
          const f = ' ' + p.f.replace(/[^a-z0-9]+/g, ' ').trim() + ' ';
          if (f.trim().length > 1 && fq.includes(f)) { hits.push({ group: g, via: p.raw }); break; }
        }
      }
      return hits;
    }
  }

  function buildQuery(q, syn) {
    const m = new Map();
    for (const t of terms(q)) m.set(t, (m.get(t) || 0) + 1);
    const recognized = syn ? syn.match(q) : [];
    for (const h of recognized) {
      for (const p of h.group.phrases) {
        for (const t of p.t) if (!m.has(t)) m.set(t, 0.45);
      }
    }
    return { terms: m, recognized };
  }

  /* Meilleur extrait (fenêtre de phrases) avec surlignage */
  function esc(s) { return (s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  function snippet(text, qterms, maxLen = 320, nSent = 1) {
    if (!text) return '';
    const sents = text.replace(/\s+/g, ' ').split(/(?<=[.;:])\s+(?=[A-ZÀ-Ý0-9«(-])/);
    const scoreS = (s) => { let x = 0; for (const t of new Set(terms(s))) if (qterms.has(t)) x += qterms.get(t); return x; };
    let best = 0, bi = 0;
    sents.forEach((s, i) => { const v = scoreS(s) + (nSent > 1 && sents[i + 1] ? scoreS(sents[i + 1]) * 0.6 : 0); if (v > best) { best = v; bi = i; } });
    let out = sents.slice(bi, bi + nSent).join(' ');
    if (out.length > maxLen * nSent) out = out.slice(0, maxLen * nSent).replace(/\s\S*$/, '') + ' …';
    return (bi > 0 ? '… ' : '') + highlight(out, qterms);
  }

  function highlight(text, qterms) {
    return text.split(/([A-Za-zÀ-ÿ0-9]+)/).map((w, i) => {
      if (i % 2 === 0) return esc(w);
      const t = stem(fold(w));
      return qterms.has(t) && !STOP.has(fold(w)) ? `<mark>${esc(w)}</mark>` : esc(w);
    }).join('');
  }

  /* ---------- sémantique (chargement à la demande) ---------- */
  const Semantic = {
    state: 'off', extractor: null, matrix: null, dim: 384, rows: [], onProgress: null,
    async enable(docs) {
      if (this.state === 'ready' || this.state === 'loading') return;
      this.state = 'loading';
      try {
        const mod = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5/+esm');
        mod.env.allowLocalModels = false;
        const files = {};
        this.extractor = await mod.pipeline('feature-extraction', 'Xenova/multilingual-e5-small', {
          dtype: 'q8',
          progress_callback: (p) => {
            if (p.status === 'progress' && p.total) { files[p.file] = [p.loaded, p.total]; }
            const v = Object.values(files); const l = v.reduce((a, x) => a + x[0], 0), t = v.reduce((a, x) => a + x[1], 0);
            if (this.onProgress && t) this.onProgress(l / t);
          },
        });
        this.load(docs);
        this.state = 'ready';
      } catch (e) {
        console.error(e);
        this.state = 'error';
        this.error = e.message || String(e);
      }
    },
    load(docs) {
      const vecs = [];
      this.rows = [];
      docs.forEach((d, i) => {
        if (!d.vec) return;
        const bin = atob(d.vec);
        if (bin.length !== this.dim) return;
        const v = new Float32Array(this.dim);
        let n = 0;
        for (let k = 0; k < this.dim; k++) { const x = (bin.charCodeAt(k) << 24) >> 24; v[k] = x; n += x * x; }
        n = Math.sqrt(n) || 1;
        for (let k = 0; k < this.dim; k++) v[k] /= n;
        vecs.push(v); this.rows.push(i);
      });
      this.matrix = vecs;
    },
    get count() { return this.rows.length; },
    async scores(q, N) {
      const out = new Float32Array(N);
      if (this.state !== 'ready' || !this.rows.length) return null;
      const r = await this.extractor(['query: ' + q], { pooling: 'mean', normalize: true });
      const qv = r.data;
      for (let j = 0; j < this.rows.length; j++) {
        const v = this.matrix[j]; let s = 0;
        for (let k = 0; k < this.dim; k++) s += v[k] * qv[k];
        out[this.rows[j]] = s;
      }
      return out;
    },
  };

  global.RegSearch = { fold, stem, tokens, terms, normNum, Index, Synonyms, buildQuery, snippet, highlight, esc, Semantic };
})(window);
