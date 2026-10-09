// Historique des filtres (propositions de la barre de recherche) : entrees les
// plus recentes d'abord, sans doublon ; une entree qui ne fait qu'affiner la
// precedente (memes jetons et plus) la remplace au lieu de s'empiler.

const MAX = 8

export function loadHistory<T>(key: string): T[] {
  try {
    const raw = JSON.parse(localStorage.getItem(key) ?? '[]')
    return Array.isArray(raw) ? (raw as T[]) : []
  } catch {
    return []
  }
}

/** Ajoute `entry` en tete ; `tokens` decrit une entree (vide = rien a retenir). */
export function pushHistory<T>(key: string, list: T[], entry: T, tokens: (e: T) => string[]): T[] {
  const tk = tokens(entry)
  if (!tk.length) return list
  const sig = (e: T) => [...tokens(e)].sort().join('\u0000')
  const mine = sig(entry)
  let rest = list.filter(e => sig(e) !== mine)
  const top = rest[0]
  if (top && tokens(top).every(t => tk.includes(t))) rest = rest.slice(1)
  const next = [entry, ...rest].slice(0, MAX)
  try { localStorage.setItem(key, JSON.stringify(next)) } catch { /* stockage indisponible */ }
  return next
}
