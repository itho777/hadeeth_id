from pathlib import Path
import struct, sys

ROOT = Path(r"G:/hadeeth_id")
NL = "\r\n"


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f"FAIL {label}: expected 1, found {n}")
        sys.exit(1)
    return text.replace(old, new)


p = ROOT / "scholars.html"
t = p.read_bytes().decode("utf-8")
old_fetch = """      let url = `${supabaseUrl}/rest/v1/rijal?select=*&hadith_count=gt.0&order=hadith_count.desc,died_ah.asc&limit=100`;
      if (activeGen === 'sahabah') url += '&is_sahabi=eq.true';
      else if (activeGen === 'tabiun') url += '&generation=eq.Tabi\\'i';
      else if (activeGen === 'collectors') url += '&generation=eq.Collector';
      if (searchQuery) url += `&or=(name_en.ilike.*${encodeURIComponent(searchQuery)}*,name_id.ilike.*${encodeURIComponent(searchQuery)}*)`;
      const res = await fetch(url, { headers: { 'apikey': anonKey, 'Authorization': `Bearer ${anonKey}` } });
      if (res.ok) {
        const data = await res.json();
        const validNarrators = (data || []).filter(r => (r.hadith_count > 0 || r.is_sahabi) && r.name_en && !r.name_en.includes('Kampung'));
        // Merge Supabase validNarrators with fallbackScholars to ensure offline/local kitabs are included
          const localScholars = filterFallbackScholars(gen, role, query);
          const merged = [...validNarrators];
          localScholars.forEach(local => {
             if (!merged.find(m => m.name_en === local.name_en || m.id === local.id)) {
                 merged.push(local);
             }
          });
          allScholars = merged;
      } else { allScholars = filterFallbackScholars(gen, role, query); }
    } catch (err) { allScholars = filterFallbackScholars(gen, role, query); }""".replace("\n", NL)
new_fetch = """      // The old Supabase `rijal` host no longer resolves. The rawis roster
      // shipped with the site is the live source; never fabricate biographies.
      const res = await fetch('data/rawis/active_rawis.min.json');
      if (res.ok) {
        const rawDict = await res.json();
        const fromRawiData = Object.keys(rawDict || {}).map(id => normalizeRawiRecord(id, rawDict[id]))
          .filter(r => r && r.hadith_count > 0 && r.name_en && !r.name_en.includes('Kampung') && matchesScholarGen(r, gen) && matchesScholarQuery(r, query));
        fromRawiData.sort((a, b) => b.hadith_count - a.hadith_count || String(a.name_en).localeCompare(String(b.name_en)));
        const localScholars = filterFallbackScholars(gen, role, query);
        const merged = [...fromRawiData];
        localScholars.forEach(local => {
          if (!merged.find(m => m.name_en === local.name_en || m.id === local.id)) merged.push(local);
        });
        allScholars = merged;
      } else { allScholars = filterFallbackScholars(gen, role, query); }
    } catch (err) { allScholars = filterFallbackScholars(gen, role, query); }""".replace("\n", NL)
t = replace_once(t, old_fetch, new_fetch, "scholars fetch")

anchor = "  function filterFallbackScholars(gen, role, query) {".replace("\n", NL)
helpers = """  function matchesScholarGen(r, gen) {
    if (gen === 'sahabah') return !!r.is_sahabi;
    if (gen === 'tabiun') return r.generation === "Tabi'i" || r.generation === "Taba' Tabi'i";
    if (gen === 'collectors') return r.generation === 'Collector';
    return true;
  }

  function matchesScholarQuery(r, query) {
    if (!query) return true;
    const q = query.toLowerCase();
    return (r.name_en || '').toLowerCase().includes(q) || (r.name_id || '').toLowerCase().includes(q);
  }

  function normalizeRawiRecord(rawId, v) {
    if (!v) return null;
    const en = String(v.en || '');
    const m = en.match(/^([\\s\\S]*?)([\\u0600-\\u06FF][\\s\\S]*)$/);
    const nameEn = (m ? m[1] : en).replace(/\\s*\\(\\s*$/, '').trim();
    const arMatch = String(v.ar || '').match(/[\\u0600-\\u06FF][\\u0600-\\u06FF\\u064B-\\u065F\\uFDFA\\s]*/);
    const nameAr = arMatch ? arMatch[0].replace(/\\s*\\(?\\s*$/, '').trim() : '';
    const grade = String(v.grade || '');
    let generation = 'Rawi';
    let isSahabi = false;
    if (grade.includes('Comp.(RA)')) { generation = 'Sahabi (Companion)'; isSahabi = true; }
    else if (grade.includes("Follower(Tabi')")) generation = "Tabi'i";
    else if (grade.includes("Succ. (Taba' Tabi')")) generation = "Taba' Tabi'i";
    else if (grade.includes("Prophet's Relative")) { generation = 'Ahl al-Bayt'; isSahabi = true; }
    else if (grade.includes('Century AH')) generation = grade.split('[')[0].trim();
    const death = String(v.death_ah || '').trim();
    return {
      id: 'rawi_' + rawId,
      name_en: nameEn,
      name_id: String(v.id || '').trim() || nameEn,
      name_ar: nameAr,
      is_sahabi: isSahabi,
      generation,
      grade: grade.split('[')[0].trim() || (isSahabi ? 'Sahabi Adl' : 'Thiqah'),
      died_ah: death && death !== '-' ? death : '',
      city_of_death: String(v.residence || '').trim(),
      hadith_count: parseInt(String(v.counts || '').replace(/[^0-9]/g, ''), 10) || 0,
      books: []
    };
  }

""".replace("\n", NL)
t = replace_once(t, anchor, helpers + anchor, "scholars helpers")
p.write_bytes(t.encode("utf-8"))
print("patched scholars.html data source")

n = 0
for p in ROOT.glob("*.html"):
    t = p.read_bytes().decode("utf-8")
    new = t.replace("js/app.js?v=20261120_sharh", "js/app.js?v=20261120_fix1")
    if new != t:
        p.write_bytes(new.encode("utf-8"))
        n += 1
print("cache-busted app.js in", n, "pages")

w = h = 16
bg = (0x6B, 0x76, 0x1A, 0xFF)
fg = (0xFF, 0xFF, 0xFF, 0xFF)
pixels = bytearray()
for y in range(h):
    for x in range(w):
        edge = x in (0, w - 1) or y in (0, h - 1)
        pixels += bytes(fg if edge else bg)
mask = bytes((h + 31) // 32 * 4 * h)
dib = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(pixels) + len(mask), 0, 0, 0, 0)
image = dib + bytes(pixels) + mask
ico = struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(image), 22) + image
(ROOT / "favicon.ico").write_bytes(ico)
print("wrote favicon.ico", len(ico), "bytes")
