with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Fix Rawi ID lookup
text = re.sub(
    r"    const isObj = typeof rawItem === 'object' && rawItem !== null;\s+const rId = isObj \? rawItem\.id : rawItem;\s+const rawiData = rawisDict\[rId\] \|\| \{\};",
    """    const isObj = typeof rawItem === 'object' && rawItem !== null;
    let rId = isObj ? rawItem.id : rawItem;
    if (typeof rId === 'number' || (typeof rId === 'string' && /^\\\\d+$/.test(rId))) {
        rId = 'lidwa_' + rId;
    }
    
    const rawiData = rawisDict[rId] || {};""",
    text
)

# Fix profile.html rendering
text = re.sub(
    r"  const rawiId = params\.get\('id'\);\s+if \(!rawiId\) \{",
    """  let rawiId = params.get('id');
  
  if (typeof rawiId === 'string' && /^\\\\d+$/.test(rawiId)) {
      rawiId = 'lidwa_' + rawiId;
  }
  
  if (!rawiId) {""",
    text
)

# Another spot in profile
text = re.sub(
    r"  let rawiIdRaw = params\.get\('id'\);\s+let rawiId = rawiIdRaw;\s+if \(!isNaN\(parseInt\(rawiIdRaw\)\)\) rawiId = rawiIdRaw;",
    """  let rawiIdRaw = params.get('id');
  let rawiId = rawiIdRaw;
  if (!isNaN(parseInt(rawiIdRaw))) rawiId = 'lidwa_' + rawiIdRaw;""",
    text
)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Patched Sanad linkages')
