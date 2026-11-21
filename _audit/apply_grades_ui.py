#!/usr/bin/env python3
"""Add grading-provenance UI and bump the app cache token. Assert every edit."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def edit(rel, fn):
    p = ROOT / rel
    raw = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    def sub(old, new, count=1):
        nonlocal text
        got = text.count(old)
        if got != count:
            print(f"ABORT {rel}: expected {count}, found {got}\n---\n{old[:300]}")
            sys.exit(1)
        text = text.replace(old, new, count)
    fn(sub)
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"patched {rel}")

helper = r'''
// ============================================================
// GRADING PROVENANCE
// Every label is reproduced from a named dataset. Missing data stays missing:
// never render a computed score or a silent 'Sahih' default.
// ============================================================
const GRADE_SOURCE_SHORT = {
  lidwa: 'Lidwa / Irsyad',
  fawaz: 'Fawaz Ahmed (sunnah.com)',
  atif_hf: 'Atif HF (sunnah.com)',
  ahmedbaset: 'AhmedBaset (Darussalam)',
  usm: 'USM (daftar Munkar)'
};

function gradeSourceGroups(gradings) {
  const groups = new Map();
  (Array.isArray(gradings) ? gradings : []).forEach(g => {
    if (!g || !g.grade) return;
    const label = g.src_label || GRADE_SOURCE_SHORT[g.src] || g.src || 'dataset';
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label).push(g);
  });
  return groups;
}

function gradeSourcesHtml(gradings) {
  const groups = gradeSourceGroups(gradings);
  if (!groups.size) return '';
  let bodies = '';
  groups.forEach((items, label) => {
    const seen = new Set();
    let values = '';
    items.forEach(g => {
      const by = String(g.by || '').trim();
      const key = by + '\u0000' + String(g.grade);
      if (seen.has(key)) return;
      seen.add(key);
      values += '<li class="leading-snug">' +
        (by ? '<span class="font-semibold">' + escapeHtml(by) + '</span> \u2014 ' : '') +
        escapeHtml(g.grade) + '</li>';
    });
    if (!values) return;
    bodies += '<div class="rounded-lg border border-outline-variant/20 dark:border-[#334155] p-3 bg-surface-container-low/40 dark:bg-[#0f172a]">' +
      '<div class="text-[11px] font-bold text-secondary dark:text-[#10b981] mb-1 break-words">' + escapeHtml(label) + '</div>' +
      '<ul class="list-disc list-inside text-xs text-on-surface-variant dark:text-gray-300 space-y-0.5">' + values + '</ul>' +
      '</div>';
  });
  if (!bodies) return '';
  const n = groups.size;
  return '<div class="rounded-xl border border-outline-variant/30 dark:border-[#334155] bg-surface dark:bg-[#1e293b] p-4 flex flex-col gap-3">' +
    '<div class="flex items-center justify-between gap-3 border-b border-outline-variant/20 dark:border-[#334155] pb-2">' +
      '<h4 class="font-bold text-xs text-primary dark:text-white">' +
        '<span data-lang-en>Grading sources</span><span data-lang-id style="display:none">Sumber penilaian</span>' +
      '</h4>' +
      '<span class="text-[10px] font-semibold text-outline dark:text-gray-400">' +
        '<span data-lang-en>' + n + ' sources</span><span data-lang-id style="display:none">' + n + ' sumber</span>' +
      '</span>' +
    '</div>' +
    '<div class="grid grid-cols-1 md:grid-cols-2 gap-2">' + bodies + '</div>' +
    '<p class="text-[10px] text-outline dark:text-gray-400 leading-snug">' +
      '<span data-lang-en>Labels are quoted from the named datasets; this site issues no independent ruling.</span>' +
      '<span data-lang-id style="display:none">Label dikutip dari dataset yang disebut; situs ini tidak menetapkan hukum sendiri.</span>' +
    '</p>' +
  '</div>';
}

function renderGradeSources(host, gradings) {
  if (!host) return;
  const html = gradeSourcesHtml(gradings);
  if (!html) {
    host.innerHTML = '';
    host.style.display = 'none';
    return;
  }
  host.innerHTML = html;
  host.style.display = 'block';
  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}

'''

def app(sub):
    sub("}\n\n// ============================================================\n// LANGUAGE SYSTEM\n",
        "}\n\n" + helper + "// ============================================================\n// LANGUAGE SYSTEM\n")
    sub("  if (!data) {\n    container.innerHTML = `<div class=\"p-8 text-center text-red-500\">Failed to load Hadith ${bookId}:${hadithId} from ${activeDsLabel}</div>`;\n    return;\n  }\n\n  // Extract variables\n",
        "  if (!data) {\n    container.innerHTML = `<div class=\"p-8 text-center text-red-500\">Failed to load Hadith ${bookId}:${hadithId} from ${activeDsLabel}</div>`;\n    return;\n  }\n\n  renderGradeSources(document.querySelector('[data-grade-sources]'), data.gradings || []);\n\n  // Extract variables\n")
    sub("    }\n    \n    // Final Node: Collector & Author metadata\n",
        "    }\n\n    renderGradeSources(document.getElementById('sanad-grade-sources'), data && data.gradings);\n\n    // Final Node: Collector & Author metadata\n")
    sub("const gradeEn = res.grade_en || res.grade || 'Sahih';\n    const gradeId = res.grade_id || 'Shahih';",
        "const gradeEn = res.grade_en || res.grade || 'Not recorded';\n    const gradeId = res.grade_id || 'Tidak tercatat';")
    sub("const gradeEn = item.grade_en || item.grade || 'Sahih';\n      const gradeId = item.grade_id || 'Shahih';",
        "const gradeEn = item.grade_en || item.grade || 'Not recorded';\n      const gradeId = item.grade_id || 'Tidak tercatat';")
edit("js/app.js", app)

def hadith(sub):
    sub("        </button>\n      </div>\n    </div>\n\n    <!-- Full Arabic Text -->",
        "        </button>\n      </div>\n    </div>\n\n    <!-- Grading provenance, populated from data.gradings -->\n    <div data-grade-sources style=\"display:none\"></div>\n\n    <!-- Full Arabic Text -->")
edit("hadith.html", hadith)

def sanad(sub):
    sub("        </p>\n      </div>\n\n\n    </div>\n\n  </div>\n</main>",
        "        </p>\n      </div>\n\n      <div id=\"sanad-grade-sources\" style=\"display:none\"></div>\n\n    </div>\n\n  </div>\n</main>")
edit("sanad.html", sanad)

htmls = sorted(p for p in ROOT.glob("*.html") if "js/app.js?v=20261120_sanad2" in p.read_text(encoding="utf-8", errors="ignore"))
for p in htmls:
    raw = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    n = text.count("js/app.js?v=20261120_sanad2")
    text = text.replace("js/app.js?v=20261120_sanad2", "js/app.js?v=20261121_grades")
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"bumped {p.name}: {n}")
