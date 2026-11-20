#!/usr/bin/env python3
"""Remove the last same-origin data fetches from js/app.js."""
import re
from pathlib import Path

p = Path(r"G:/hadeeth_id/js/app.js")
s = p.read_text(encoding="utf-8")


def rep(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:100]!r}"
    s = s.replace(old, new, n)


# one-line baseUrl definitions (1200, 1940, 4678)
s, n = re.subn(r"const baseUrl = window\.__HADEETH_BASE__ \? window\.__HADEETH_BASE__ \+ '/data' : window\.location\.origin \+ window\.location\.pathname\.replace\(/\\/\[\^/\]\*\$/, ''\) \+ '/data';",
               "const baseUrl = window.HadeethAPI.dataUrl;", s)
print("one-line baseUrl", n)
assert n == 3

# multi-line baseUrl definitions (2061, 3460)
s, n = re.subn(r"const baseUrl = window\.__HADEETH_BASE__\s*\n\s*\? window\.__HADEETH_BASE__ \+ '/data'\s*\n\s*: \(\(\) => \{.*?\}\)\(\);",
               "const baseUrl = window.HadeethAPI.dataUrl;", s, flags=re.S)
print("multi-line baseUrl", n)
assert n == 2

# detail page: links + editions
rep("""  const [linkResp, editionsResp] = await Promise.all([
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
    fetch(`${baseUrl}/meta/fawaz_editions.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) linkGraph = await linkResp.json();
  let fawazEditions = {};
  if (editionsResp && editionsResp.ok) fawazEditions = await editionsResp.json();""",
"""  const [linkGraphData, fawazEditionsData] = await Promise.all([
    window.HadeethAPI.getLinks(bookId).catch(() => null),
    window.HadeethAPI.getFawazEditions().catch(() => null)
  ]);

  let linkGraph = linkGraphData || {};
  let fawazEditions = fawazEditionsData || {};""")

# branch B: link map
rep("""          const [linkResp, lidwaData] = await Promise.all([
            fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
            window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null)
          ]);

          if (linkResp && linkResp.ok) {
            const linkData = await linkResp.json();""",
"""          const [linkGraphData, lidwaData] = await Promise.all([
            window.HadeethAPI.getLinks(bookId).catch(() => null),
            window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null)
          ]);

          if (linkGraphData) {
            const linkData = linkGraphData;""")

# branch B fallback: links + AhmedBaset by_book
rep("""      const [lidwaData, linkResp, abResp] = await Promise.all([
          window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null),
          fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null),
          fetch(`${baseUrl}/sources/ahmedbaset/by_book/${abBook}.json`).catch(() => null)
      ]);

      if (linkResp && linkResp.ok) linkGraph = await linkResp.json();""",
"""      const [lidwaData, linkGraphData, abData] = await Promise.all([
          window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null),
          window.HadeethAPI.getLinks(bookId).catch(() => null),
          fetch(`${window.HadeethAPI.dataUrl}/sources/ahmedbaset/by_book/${abBook}.json`).catch(() => null)
      ]);

      if (linkGraphData) linkGraph = linkGraphData;""")
rep("""      if (abResp && abResp.ok) {
        const abData = await abResp.json();
        (abData.hadiths || []).forEach(h => {""",
"""      if (abData) {
        (abData.hadiths || []).forEach(h => {""")

# branch C: AhmedBaset by_chapter
rep("""      const resp = await fetch(`data/sources/ahmedbaset/by_chapter/${abBook}/${chapterId}.json`);""",
    """      const resp = await fetch(`${window.HadeethAPI.dataUrl}/sources/ahmedbaset/by_chapter/${abBook}/${chapterId}.json`);""")

# branch C: AhmedBaset by_book
rep("""      const resp = await fetch(`data/sources/ahmedbaset/by_book/${abBook}.json`);""",
    """      const resp = await fetch(`${window.HadeethAPI.dataUrl}/sources/ahmedbaset/by_book/${abBook}.json`);""")

# branch C: lidwa chapter envelope
rep("""      const resp = await fetch(`data/lidwa-chapters/${bookId}.json`);
      if (resp.ok) lidwaIndex = await resp.json();""",
"""      lidwaIndex = await window.HadeethAPI.getLidwaChapters(bookId);""")

# detail page translations: links
rep("""  const [engEdition, araEdition, linkResp] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ara', bookId).catch(() => null),
    fetch(`${baseUrl}/links/${bookId}.json`).catch(() => null)
  ]);

  let linkGraph = {};
  if (linkResp && linkResp.ok) {
    linkGraph = await linkResp.json();
  }""",
"""  const [engEdition, araEdition, linkGraphData] = await Promise.all([
    window.HadeethAPI.getEdition('eng', bookId).catch(() => null),
    window.HadeethAPI.getEdition('ara', bookId).catch(() => null),
    window.HadeethAPI.getLinks(bookId).catch(() => null)
  ]);

  let linkGraph = linkGraphData || {};""")

# topic page: topic metadata
rep("""      const topics = await (window.HadeethAPI && window.HadeethAPI.getTopics
        ? window.HadeethAPI.getTopics()
        : fetch('data/api/topics_metadata.ndjson').then(r => r.text())
            .then(t => t.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line))));""",
"""      const topics = await window.HadeethAPI.getTopics();""")

# topic page: index fallback
rep("""      const idxRes = await fetch('data/api/topics_index.json?v=20260826_1');
      const idxData = await idxRes.json();""",
"""      const idxData = await window.HadeethAPI.getTopicIndex();""")

# topic page: links cache
rep("""        const resp = await fetch(`${baseUrl}/links/${bookId}.json`);
        if (resp.ok) window[cacheKey] = await resp.json();""",
"""        const graph = await window.HadeethAPI.getLinks(bookId);
        if (graph) window[cacheKey] = graph;""")

p.write_text(s, encoding="utf-8", newline="\r\n")
print("patched js/app.js")
