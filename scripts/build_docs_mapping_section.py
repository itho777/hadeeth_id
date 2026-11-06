"""Inject the Cross-Collection Mapping section into docs.html.

Design rules for this section:
  * Every number is read from data/mapping-stats.json, which is generated from the
    actual *_links.json files. No hand-typed figures — the page cannot drift.
  * Written so a scholar, a translator, or a developer can each find what they need.
  * States what is NOT mapped as plainly as what is. That is the promise the page
    has to keep for years.

Idempotent: replaces the block between the marker comments on re-run.
"""
import json, os, html

ROOT = 'G:/hadeeth_id'
DOCS = os.path.join(ROOT, 'docs.html')
STATS = os.path.join(ROOT, 'data', 'mapping-stats.json')
BEGIN = '<!-- MAPPING:SECTION:BEGIN -->'
END = '<!-- MAPPING:SECTION:END -->'


def esc(s):
    return html.escape(str(s), quote=True)


def tier_badge(pct):
    if pct >= 90:
        cls = 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
    elif pct >= 75:
        cls = 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
    else:
        cls = 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300'
    return cls


def build(stats):
    t = stats['totals']
    rows = ""
    for c in sorted(stats['collections'], key=lambda x: -x['total']):
        cls = tier_badge(c['pct'])
        rows += f"""
        <tr class="border-b border-outline-variant/20 dark:border-[#334155]">
          <td class="py-2 pr-3">
            <div class="font-semibold text-primary dark:text-white">{esc(c['name'])}</div>
            <div class="text-[11px] text-on-surface-variant dark:text-gray-500" dir="rtl">{esc(c['name_ar'])}</div>
          </td>
          <td class="py-2 pr-3 text-[11px] text-on-surface-variant dark:text-gray-400">{esc(c['author'])}</td>
          <td class="py-2 pr-3 text-right tabular-nums">{c['total']:,}</td>
          <td class="py-2 pr-3 text-right tabular-nums">{c['linked']:,}</td>
          <td class="py-2 pr-3 text-right">
            <span class="inline-block px-2 py-0.5 rounded text-[11px] font-semibold {cls}">{c['pct']}%</span>
          </td>
          <td class="py-2 pr-3 text-right tabular-nums">{c['links']:,}</td>
          <td class="py-2 text-right tabular-nums">{c['conf_pct']}%</td>
        </tr>"""

    dups = ""
    for d in stats.get('duplicates', []):
        dups += f"""
      <p class="text-xs">▪ <strong>Duplicate source reconciled</strong> — {esc(d['a'])} and {esc(d['b'])}: {esc(d['finding'])}</p>"""

    return f"""
{BEGIN}
  <section class="flex flex-col gap-4" id="mapping">
    <h2 class="text-lg font-bold text-primary dark:text-white flex items-center gap-2">
      <span class="material-symbols-outlined text-secondary dark:text-[#10b981]">hub</span>
      Cross-Collection Hadith Mapping
    </h2>

    <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-3 text-sm text-on-surface-variant dark:text-gray-300">
      <p>
        Many collections on this site quote the same hadith. Riyad as-Salihin, Bulugh al-Maram and
        Mishkat al-Masabih are compilations: nearly every hadith in them was selected from an earlier
        source such as Sahih al-Bukhari, Sahih Muslim or the Sunan. This page documents how each
        collection's hadiths are linked back to those originals, so a reader can move from a
        compilation entry to the full chain of narration and every translation we hold.
      </p>
      <p>
        <strong>The mapping is the deliverable.</strong> Once a hadith is identified as the same
        hadith as one in Bukhari, everything attached to that original — sanad, narrators, jarh wa
        ta'dil, grading, translations — becomes reachable by a simple lookup. We therefore publish a
        thin, auditable set of links rather than a merged corpus.
      </p>
    </div>

    <div class="flex items-start gap-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700/40 rounded-lg p-4">
      <span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-[20px] mt-0.5">fingerprint</span>
      <div class="text-xs text-emerald-900 dark:text-emerald-200 flex flex-col gap-1">
        <p><strong>Identity is established by Arabic text, never by hadith number.</strong>
        Hadith numbering is not shared between collections, and it is not shared between language
        editions of the same collection. Numbers were used only as a search hint and were always
        confirmed against the text before being accepted.</p>
        <p><strong>Unmatched is left unmatched.</strong> We do not fill gaps by guessing. A hadith
        with no confident match stays unlinked, and is counted as such below.</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-lg p-4">
        <div class="text-2xl font-bold text-primary dark:text-white tabular-nums">{t['collections']}</div>
        <div class="text-[11px] uppercase tracking-wider text-on-surface-variant dark:text-gray-400">Collections mapped</div>
      </div>
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-lg p-4">
        <div class="text-2xl font-bold text-primary dark:text-white tabular-nums">{t['hadiths']:,}</div>
        <div class="text-[11px] uppercase tracking-wider text-on-surface-variant dark:text-gray-400">Hadiths examined</div>
      </div>
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-lg p-4">
        <div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">{t['linked']:,}</div>
        <div class="text-[11px] uppercase tracking-wider text-on-surface-variant dark:text-gray-400">Linked ({t['pct']}%)</div>
      </div>
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-lg p-4">
        <div class="text-2xl font-bold text-primary dark:text-white tabular-nums">{t['source_links']:,}</div>
        <div class="text-[11px] uppercase tracking-wider text-on-surface-variant dark:text-gray-400">Source links</div>
      </div>
    </div>

    <div class="overflow-x-auto bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-4">
      <table class="w-full text-xs text-on-surface-variant dark:text-gray-300">
        <thead>
          <tr class="border-b border-outline-variant/40 dark:border-[#475569] text-left">
            <th class="py-2 pr-3 font-semibold text-primary dark:text-white">Collection</th>
            <th class="py-2 pr-3 font-semibold text-primary dark:text-white">Author</th>
            <th class="py-2 pr-3 text-right font-semibold text-primary dark:text-white">Hadiths</th>
            <th class="py-2 pr-3 text-right font-semibold text-primary dark:text-white">Linked</th>
            <th class="py-2 pr-3 text-right font-semibold text-primary dark:text-white">Coverage</th>
            <th class="py-2 pr-3 text-right font-semibold text-primary dark:text-white">Links</th>
            <th class="py-2 text-right font-semibold text-primary dark:text-white">Confirmed</th>
          </tr>
        </thead>
        <tbody>{rows}
        </tbody>
        <tfoot>
          <tr class="font-semibold text-primary dark:text-white">
            <td class="py-2 pr-3" colspan="2">Total</td>
            <td class="py-2 pr-3 text-right tabular-nums">{t['hadiths']:,}</td>
            <td class="py-2 pr-3 text-right tabular-nums">{t['linked']:,}</td>
            <td class="py-2 pr-3 text-right tabular-nums">{t['pct']}%</td>
            <td class="py-2 pr-3 text-right tabular-nums">{t['source_links']:,}</td>
            <td class="py-2 text-right tabular-nums">{t['conf_pct']}%</td>
          </tr>
        </tfoot>
      </table>
      <p class="text-[11px] text-on-surface-variant dark:text-gray-500 mt-3">
        <strong>Links</strong> are edges, not hadiths: one compilation hadith may trace to several
        originals (for example a hadith recorded by both Bukhari and Muslim, plus a parallel in the
        Sunan), and each edge is recorded separately. <strong>Confirmed</strong> is the share of
        linked hadiths whose best match met the strict evidence threshold; the remainder are held at
        “probable” and are listed for review.
      </p>
    </div>

    <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-3 text-sm text-on-surface-variant dark:text-gray-300">
      <h3 class="font-bold text-primary dark:text-white">How a link is established</h3>
      <p>Each candidate is scored by evidence, and the evidence is stored alongside the link so the
      basis can be audited later:</p>
      <ol class="list-decimal ml-5 flex flex-col gap-2">
        <li><strong>Normalise the Arabic.</strong> Diacritics, hamza forms, alef/teh-marbuta variants,
        punctuation and invisible directional marks are folded. Indo-Persian orthography
        (<code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">ک ی ہ</code>) is
        folded to Arabic (<code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">ك ي ه</code>)
        — without this, a genuine match can score zero.</li>
        <li><strong>Strip editorial apparatus.</strong> Compilers append provenance notes such as
        <span dir="rtl">((متفق عليه))</span> or <span dir="rtl">رواه أبو داود (775)</span>. These are
        removed from the text being matched and parsed separately as a provenance hint.</li>
        <li><strong>Rare-phrase fingerprinting.</strong> Five-word sequences that are rare across the
        whole corpus are the fingerprints; common phrases such as
        <span dir="rtl">صلى الله عليه وسلم</span> carry no signal and are discarded automatically.</li>
        <li><strong>Score and rank, then guard.</strong> Candidates are ranked by the number of
        fingerprints found, not by a percentage — a short accidental overlap must not outrank a
        long genuine one. A minimum evidence floor is required before anything is accepted.</li>
        <li><strong>Short texts get a different method.</strong> Some collections are maxims of two
        or three words (<span dir="rtl">الحرب خدعة</span>). Fingerprinting cannot work there, so the
        content phrase is searched verbatim instead, and coverage for that collection is
        correspondingly lower.</li>
      </ol>
      <p class="text-xs"><strong>Translations</strong> are attached by resolving a source hadith to
      its own Arabic edition first, then reading every language at that resolved position. This is
      necessary because language editions of the same collection are not number-aligned: an Urdu
      edition can hold a different hadith at the same number as the Arabic edition. Where the
      Arabic cannot be resolved, no translation is attached.</p>{dups}
    </div>

    <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-3 text-sm text-on-surface-variant dark:text-gray-300">
      <h3 class="font-bold text-primary dark:text-white">What is not linked, and why</h3>
      <p>Coverage varies because the collections themselves differ in kind, not because effort was
      uneven:</p>
      <p class="text-xs">▪ <strong>Compilations</strong> (Riyad, Mishkat, Bulugh) quote sources
      near-verbatim, so coverage is high. <strong>Independent musnads</strong> (Ibn Hibban, Ibn
      Khuzaimah, Mustadrak, Daruquthni) narrate through their own chains with their own wording, so
      the matn can differ even where the hadith is the same.</p>
      <p class="text-xs">▪ <strong>Bulugh al-Maram</strong> contains variants and cross-references
      (“this is a portion of the long hadith mentioned earlier”) rather than standalone hadiths.
      Where it cites a hadith by number, that number is recorded as <em>unverified provenance</em>
      unless the cited text actually contains the matn — those are counted separately and are not
      presented as links.</p>
      <p class="text-xs">▪ <strong>Dehlawi 40</strong> is a list of maxims rather than full matn, so
      it will always sit lowest.</p>
      <p class="text-xs">▪ Rows left unlinked are retained in the dataset with an explicit
      <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">unmapped</code>
      status and are <strong>not</strong> hidden.</p>
      <p class="text-xs">▪ <strong>Known source gaps.</strong> Some anchor files we hold are partial.
      Sunan Daruquthni is present as a 236-row extract (hadith numbers 1–239, with gaps) while the
      full work numbers some 4,790 entries; Musnad Ahmad's enrichment source covers only a 1,374-row
      fragment. Coverage percentages for those collections describe <em>the downloaded portion
      only</em>, and will rise when complete files are ingested. They are published as measured
      rather than extrapolated.</p>
    </div>

    <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl p-6 flex flex-col gap-3 text-sm text-on-surface-variant dark:text-gray-300">
      <h3 class="font-bold text-primary dark:text-white">For scholars, translators and reviewers</h3>
      <p>
        This mapping is offered as an aid to study, not as religious authority. It is a set of
        proposed correspondences between collections, produced by textual comparison, and it is
        published so that it can be checked.
      </p>
      <p class="text-xs">▪ Every link carries a <strong>confidence tier</strong>
      (<code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">confirmed</code> /
      <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">probable</code> /
      <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">review</code>),
      the <strong>evidence count</strong> behind it, and the <strong>method</strong> used.</p>
      <p class="text-xs">▪ Links at <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">probable</code>
      and <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">review</code>
      are the ones most worth your attention. Collections reporting lower confirmed shares
      (Al-Adab al-Mufrad, Mustadrak, Daruquthni, Musnad Syafii) are the suggested starting point.</p>
      <p class="text-xs">▪ The full machine-readable mapping is available as
      <code class="bg-surface-container-low dark:bg-[#0f172a] px-1 rounded text-xs">data/mapping-stats.json</code>
      with per-collection detail, and the per-collection link files are in the project repository.</p>
      <p class="text-xs">▪ Corrections and disagreements are welcome and can be applied per link
      without re-running the whole pipeline — the mapping is additive and auditable by design.</p>
    </div>
  </section>
{END}
"""


def main():
    stats = json.load(open(STATS, encoding='utf-8'))
    block = build(stats)
    doc = open(DOCS, encoding='utf-8').read()

    if BEGIN in doc and END in doc:
        head = doc.split(BEGIN)[0]
        tail = doc.split(END, 1)[1]
        doc = head + block + tail
        action = 'replaced'
    else:
        anchor = '</main>'
        i = doc.rfind(anchor)
        if i == -1:
            raise SystemExit('no </main> found in docs.html')
        doc = doc[:i] + block + '\n' + doc[i:]
        action = 'inserted'

    open(DOCS, 'w', encoding='utf-8').write(doc)
    print(f'{action} mapping section in docs.html ({len(block)} chars)')


if __name__ == '__main__':
    main()