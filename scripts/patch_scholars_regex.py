import re

with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = r"allScholars = validNarrators\.length > 0 \? validNarrators : filterFallbackScholars\(gen, role, query\);"

replacement = """
          // Merge Supabase validNarrators with fallbackScholars to ensure offline/local kitabs are included
          const localScholars = filterFallbackScholars(gen, role, query);
          const merged = [...validNarrators];
          localScholars.forEach(local => {
             if (!merged.find(m => m.name_en === local.name_en || m.id === local.id)) {
                 merged.push(local);
             }
          });
          allScholars = merged;
"""

if re.search(target, html):
    html = re.sub(target, replacement.strip(), html)
    with open('scholars.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Patched scholars.html successfully via Regex.")
else:
    print("Target regex not found.")
