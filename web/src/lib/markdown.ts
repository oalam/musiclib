// Rendu markdown des notes du vault (Knowledge, notebooks du sound design) :
// HTML brut echappe, liens externes dans un nouvel onglet, ancres de titre
// = slugify (meme regle que kb.py).

import { Marked } from 'marked'
import { slugify } from './api'

export const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

export function createMarked(): Marked {
  return new Marked({
    renderer: {
      html({ text }) { return escapeHtml(text) },
      // liens externes : nouvel onglet, sinon l'app est remplacee
      link({ href, title, tokens }) {
        const ext = /^https?:\/\//.test(href)
        return `<a href="${escapeHtml(href)}"${title ? ` title="${escapeHtml(title)}"` : ''}${ext ? ' target="_blank" rel="noopener"' : ''}>${this.parser.parseInline(tokens)}</a>`
      },
      heading({ tokens, depth, text }) {
        return `<h${depth} id="${slugify(text)}">${this.parser.parseInline(tokens)}</h${depth}>`
      },
    },
  })
}

/** Wikilinks Obsidian `[[cible|alias]]` remplaces par `render(cible, alias)`. */
export function replaceWikilinks(md: string, render: (target: string, alias: string) => string): string {
  return md.replace(/\[\[([^\]|]+)\|?([^\]]*)\]\]/g, (_, target: string, alias: string) => render(target, alias))
}
