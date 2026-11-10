// Faux grist-plugin-api.js pour les tests : document en mémoire conservé dans la fenêtre parente.
(function () {
  const top = window.top;
  const db = top.__db || (top.__db = { T: {}, next: 1, actions: 0 });
  const toCols = (rows) => { const keys = new Set(['id']); rows.forEach((r) => Object.keys(r).forEach((k) => keys.add(k))); const o = {}; keys.forEach((k) => (o[k] = rows.map((r) => (k in r ? r[k] : null)))); return o; };
  const isDate = (k) => /^(En_vigueur_depuis|Fin_de_vigueur|Date_a_venir|Derniere_modif_texte|Mis_a_jour|Date|Date_effet)$/.test(k);
  function check(tb, rec) { for (const k in rec) if (isDate(k) && rec[k] != null && typeof rec[k] !== 'number') throw new Error(`date non numérique ${tb}.${k}=${rec[k]}`); }
  window.grist = {
    ready() {}, onRecords(cb) { db.cb = cb; }, onRecord() {},
    docApi: {
      async listTables() { return Object.keys(db.T); },
      async fetchTable(t) { if (!db.T[t]) throw new Error('KeyError ' + t); return toCols(db.T[t]); },
      async getAccessToken() { return { token: 'x', baseUrl: 'http://localhost:8765/fake', ttlMsecs: 300000 }; },
      async applyUserActions(actions) {
        const ret = []; db.actions += actions.length;
        for (const a of actions) {
          const [op, tb] = a;
          if (op === 'AddTable') { db.T[tb] = []; ret.push(null); }
          else if (op === 'ModifyColumn') ret.push(null);
          else if (op === 'AddRecord') { check(tb, a[3]); const id = db.next++; const r = { id, ...a[3] }; if (tb === 'REG_Commentaires') { r.Auteur = 'Agent Test'; r.Auteur_email = 'agent@test'; r.Cree_le = Date.now() / 1000; } db.T[tb].push(r); ret.push(id); }
          else if (op === 'BulkAddRecord') { const ids = []; a[2].forEach((_, i) => { const id = db.next++; const r = { id }; for (const k in a[3]) r[k] = a[3][k][i]; check(tb, r); db.T[tb].push(r); ids.push(id); }); ret.push(ids); }
          else if (op === 'UpdateRecord') { check(tb, a[3]); Object.assign(db.T[tb].find((r) => r.id === a[2]), a[3]); ret.push(null); }
          else if (op === 'BulkUpdateRecord') { a[2].forEach((id, i) => { const r = db.T[tb].find((x) => x.id === id); for (const k in a[3]) r[k] = a[3][k][i]; check(tb, r); }); ret.push(null); }
          else throw new Error('action ' + op);
        }
        return { retValues: ret };
      },
    },
  };
})();
