with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          narratorEn = data.rawis[0].name_en || data.rawis[0].ar;
          narratorId = data.rawis[0].name_id || data.rawis[0].ar;"""

replacement = """          narratorEn = data.rawis[0].name_en || data.rawis[0].name || data.rawis[0].ar || "Unknown Transmitter";
          narratorId = data.rawis[0].name_id || data.rawis[0].name || data.rawis[0].ar || "Perawi Tidak Diketahui";"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched sahabi preview')
else:
    print('Target not found')
