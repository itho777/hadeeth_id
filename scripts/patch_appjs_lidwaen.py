import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

lidwa_block = """  // Inject Lidwa translation via Master Link Engine for Indonesian fallback
  if (lidwaId || activeDataset === 'native_lidwa') {
      translationOptions.push({
          id: 'lidwa-id',
          label: `ID - Kemenag (Lidwa)`,
          lang: 'Indonesian',
          source: 'lidwa_id',
          hid: lidwaId || hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.ndjson`
      });
      translationOptions.push({
          id: 'lidwa-en',
          label: `EN - Kemenag (Lidwa)`,
          lang: 'English',
          source: 'lidwa_en',
          hid: lidwaId || hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.ndjson`
      });
  }"""

# Use regex to find and replace the block
text = re.sub(
    r"  // Inject Lidwa translation via Master Link Engine for Indonesian fallback\s+if \(lidwaId \|\| activeDataset === 'native_lidwa'\) \{\s+translationOptions\.push\(\{\s+id: 'lidwa-id',\s+label: `ID - Kemenag \(Lidwa\)`,\s+lang: 'Indonesian',\s+source: 'lidwa',\s+hid: lidwaId \|\| hadithId,\s+file: `\$\{baseUrl\}/sources/lidwa/\$\{bookId\}\.ndjson`\s+\}\);\s+\}",
    lidwa_block,
    text
)

text = re.sub(
    r"if \(opt\.source === 'lidwa' && data\.text_id\) return data\.text_id;",
    "if (opt.source === 'lidwa_id' && data.text_id) return data.text_id;\n      if (opt.source === 'lidwa_en' && data.text_en) return data.text_en;",
    text
)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
