import re

text = open('js/app.js', encoding='utf-8').read()

text = text.replace("const label = isId ? ds.labelId : ds.label;", "")
text = text.replace("${escapeHtml(label)}", "<span data-lang-en>${escapeHtml(ds.label)}</span><span data-lang-id style=\"display:none\">${escapeHtml(ds.labelId)}</span>")

# Also fix activeLabel, activeSources, activeNote
text = text.replace("const activeLabel = isId ? activeDs.labelId : activeDs.label;", "")
text = text.replace("const activeSources = isId ? activeDs.sourcesId : activeDs.sources;", "")
text = text.replace("const activeNote = isId ? activeDs.noteId : activeDs.note;", "")

text = text.replace("${escapeHtml(activeLabel)}", "<span data-lang-en>${escapeHtml(activeDs.label)}</span><span data-lang-id style=\"display:none\">${escapeHtml(activeDs.labelId)}</span>")
text = text.replace("${escapeHtml(activeSources)}", "<span data-lang-en>${escapeHtml(activeDs.sources)}</span><span data-lang-id style=\"display:none\">${escapeHtml(activeDs.sourcesId)}</span>")
text = text.replace("${escapeHtml(activeNote)}", "<span data-lang-en>${escapeHtml(activeDs.note)}</span><span data-lang-id style=\"display:none\">${escapeHtml(activeDs.noteId)}</span>")

open('js/app.js', 'w', encoding='utf-8').write(text)
