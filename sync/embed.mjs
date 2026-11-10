// Calcule les vecteurs sémantiques des articles (modèle multilingual-e5-small, exécuté localement).
// Seuls les articles nouveaux ou modifiés sont recalculés.
// Usage : node embed.mjs ../data/reglementation.json ../data/vecteurs.json
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pipeline } from '@huggingface/transformers';

const [, , dataPath = '../data/reglementation.json', vecPath = '../data/vecteurs.json'] = process.argv;
const nodes = JSON.parse(readFileSync(dataPath, 'utf8'));
const vec = existsSync(vecPath) ? JSON.parse(readFileSync(vecPath, 'utf8')) : {};

const empreinte = (n) => createHash('sha1')
  .update((n.Numero || '') + (n.Chemin || '') + (n.Titre || '') + (n.Texte || '') + (n.Version_a_venir || ''), 'utf8')
  .digest('hex').slice(0, 12);

export function passage(n) {
  const chemin = (n.Chemin || '').split(' › ').slice(-2).join(' › ');
  const corps = (n.Texte || n.Version_a_venir || '').replace(/\s+/g, ' ').slice(0, 1600);
  return `passage: Article ${n.Numero}. ${chemin}. ${corps}`;
}

function quantifie(v) {
  let m = 0;
  for (const x of v) m = Math.max(m, Math.abs(x));
  const q = new Int8Array(v.length);
  for (let i = 0; i < v.length; i++) q[i] = Math.round((v[i] / (m || 1)) * 127);
  return Buffer.from(q.buffer).toString('base64');
}

const todo = nodes.filter((n) => n.Type === 'Article' && (!vec[n.Identifiant] || vec[n.Identifiant].h !== empreinte(n)));
console.log(`${todo.length} article(s) à vectoriser sur ${nodes.filter((n) => n.Type === 'Article').length}`);
if (todo.length) {
  const ext = await pipeline('feature-extraction', 'Xenova/multilingual-e5-small', { dtype: 'q8' });
  const B = 16;
  for (let i = 0; i < todo.length; i += B) {
    const lot = todo.slice(i, i + B);
    const out = await ext(lot.map(passage), { pooling: 'mean', normalize: true });
    out.tolist().forEach((v, j) => { vec[lot[j].Identifiant] = { h: empreinte(lot[j]), v: quantifie(v) }; });
    if ((i / B) % 20 === 0) console.log(`  ${Math.min(i + B, todo.length)}/${todo.length}`);
  }
}
// on ne garde que les articles encore présents
const ids = new Set(nodes.map((n) => n.Identifiant));
for (const k of Object.keys(vec)) if (!ids.has(k)) delete vec[k];
writeFileSync(vecPath, JSON.stringify(vec));
for (const n of nodes) if (vec[n.Identifiant]) n.Vecteur = vec[n.Identifiant].v;
writeFileSync(dataPath, JSON.stringify(nodes));
console.log('ok');
