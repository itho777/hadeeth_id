#!/usr/bin/env python3
"""Move every remaining page fetch onto R2 NDJSON."""
from pathlib import Path

ROOT = Path(r"G:/hadeeth_id")


def edit(name, pairs):
    p = ROOT / name
    s = p.read_text(encoding="utf-8")
    for old, new, n in pairs:
        assert s.count(old) == n, f"{name}: expected {n}, found {s.count(old)}: {old[:80]!r}"
        s = s.replace(old, new, n)
    p.write_text(s, encoding="utf-8", newline="\r\n")
    print("patched", name)


BOOKS_OLD = """      const res = await fetch('data/books_v2.json?v=' + Date.now());
      const data = await res.json();"""
BOOKS_NEW = """      const data = await window.HadeethAPI.getBooks();"""

for f in ("books.html", "books2.html"):
    edit(f, [
        (BOOKS_OLD, BOOKS_NEW, 1),
        ('console.error("Failed to load books_v2.json", e);', 'console.error("Failed to load books from R2", e);', 1),
    ])

edit("topics.html", [
    ("""            const response = await fetch('data/api/topics_metadata.ndjson');
            if (!response.ok) throw new Error('Failed to load topics');
            const text = await response.text();
            const topics = text.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line));""",
     """            const topics = await window.HadeethAPI.getTopics();
            if (!topics.length) throw new Error('Failed to load topics');""", 1),
])

edit("topics-in-kitab.html", [
    ("""            const topicRes = await fetch('data/api/topics_metadata.ndjson');
            const topicText = await topicRes.text();
            const topics = topicText.trim().split('\\n').filter(l => l.trim()).map(line => JSON.parse(line));""",
     """            const topics = await window.HadeethAPI.getTopics();""", 1),
    ("""            const booksRes = await fetch('data/books_v2.json?v=' + Date.now());
            const books = await booksRes.json();""",
     """            const books = await window.HadeethAPI.getBooks();""", 1),
    ("""                const countsRes = await fetch('data/api/topics_counts.json');
                counts = await countsRes.json();""",
     """                counts = await window.HadeethAPI.getTopicsCounts();""", 1),
])

edit("glossary.html", [
    ("""            const response = await fetch('data/api/glossary.json');
            if (!response.ok) {
                // If the file doesn't exist yet, we will just use an empty array.
                allTerms = [];
            } else {
                allTerms = await response.json();
            }""",
     """            allTerms = await window.HadeethAPI.getGlossary();""", 1),
])

edit("admin.html", [
    ("""        const res = await fetch('data/api/glossary.json');

        if (res.ok) existing = await res.json();""",
     """        existing = await window.HadeethAPI.getGlossary();""", 10),
])

edit("scholars.html", [
    ("""      const res = await fetch('data/rawis/active_rawis.min.json');
      if (res.ok) {
        const rawDict = await res.json();""",
     """      const rawDict = await window.HadeethAPI.getActiveRawis();
      if (rawDict && Object.keys(rawDict).length) {""", 1),
])

edit("profile-detail.html", [
    ("""      // Try fetching from the dynamically created profiles folder first
      let rawi = null;
      try {
          const res = await fetch(`data/rawis/profiles/${rawiIdRaw}.json`);
          if (res.ok) rawi = await res.json();
      } catch (e) {}

      if (!rawi) {
          const rawisDict = await window.HadeethAPI.getActiveRawis();
          rawi = rawisDict[rawiId] || await window.HadeethAPI.getRawiProfile(rawiId);
      }""",
     """      // One byte range out of rawis/profiles.ndjson on R2.
      let rawi = null;
      try {
          rawi = await window.HadeethAPI.getRawiProfile(rawiIdRaw);
      } catch (e) {}

      if (!rawi) {
          const rawisDict = await window.HadeethAPI.getActiveRawis();
          rawi = rawisDict[rawiId] || null;
      }""", 1),
])

edit("master-link-viewer.html", [
    ("""        const response = await fetch('data/links/master_link.json');
        masterData = await response.json();""",
     """        masterData = await window.HadeethAPI.getLinks('master_link') || {};""", 1),
    ('console.error("Failed to load master_link.json", err);',
     'console.error("Failed to load master_link from R2", err);', 1),
])

edit("node_diagram.html", [
    ("""        const response = await fetch('data/links/bukhari.json');
        const data = await response.json();""",
     """        const data = await window.HadeethAPI.getLinks('bukhari') || {};""", 1),
])
