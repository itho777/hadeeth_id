import os
import re
import json

# 1. Extract fallbackScholars from scholars.html
with open('scholars.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Try to extract the block
match = re.search(r'const fallbackScholars = \[(.*?)\];', html, re.DOTALL)
if match:
    block = match.group(1)
    # This block has JS objects like: { id: 'rawi_umar_ibn_al_khattab', name_en: "...", ... }
    # Let's extract them manually using regex
    objects = re.findall(r'\{(.*?)\}', block, re.DOTALL)
    
    os.makedirs('data/rawis/profiles', exist_ok=True)
    
    for obj_str in objects:
        # Extract fields
        obj = {}
        for field in ['id', 'name_en', 'name_id', 'name_ar', 'is_sahabi', 'generation', 'grade', 'died_ah', 'died_ce', 'hadith_count', 'city_of_death', 'bio_en']:
            # Find field: "value" or field: 'value' or field: value
            f_match = re.search(r'\b' + field + r'\s*:\s*(?:\"(.*?)\"|\'(.*?)\'|([^,]+))', obj_str)
            if f_match:
                val = f_match.group(1) if f_match.group(1) is not None else (f_match.group(2) if f_match.group(2) is not None else f_match.group(3))
                if val is not None:
                    obj[field] = val.strip()
        
        # Array fields like books: ["A", "B"]
        books_match = re.search(r'books\s*:\s*\[(.*?)\]', obj_str)
        if books_match:
            books_str = books_match.group(1)
            obj['books'] = [x.strip(' "\'') for x in books_str.split(',') if x.strip()]
        else:
            obj['books'] = []
            
        # Write to JSON file
        if 'id' in obj:
            with open(f"data/rawis/profiles/{obj['id']}.json", 'w', encoding='utf-8') as f:
                json.dump(obj, f, indent=2, ensure_ascii=False)
            print(f"Created profile JSON for {obj['id']}")

# 2. Inject rendering logic into profile-detail.html
with open('profile-detail.html', 'r', encoding='utf-8') as f:
    detail_html = f.read()

# Only inject if it doesn't already exist
if 'renderProfileData' not in detail_html:
    inject_script = """
<script>
  async function renderProfileData() {
      const params = new URLSearchParams(window.location.search);
      let rawiIdRaw = params.get('id') || params.get('name') || 'rawi_abu_hurairah';
      let rawiId = rawiIdRaw.startsWith('rawi_') ? (isNaN(parseInt(rawiIdRaw.split('_')[1])) ? rawiIdRaw : rawiIdRaw.split('_')[1]) : rawiIdRaw;
      if (!isNaN(parseInt(rawiIdRaw))) rawiId = rawiIdRaw;

      // Try fetching from the dynamically created profiles folder first
      let rawi = null;
      try {
          const res = await fetch(`data/rawis/profiles/${rawiIdRaw}.json`);
          if (res.ok) rawi = await res.json();
      } catch (e) {}

      if (!rawi) {
          const rawisDict = await window.HadeethAPI.getActiveRawis();
          rawi = rawisDict[rawiId] || await window.HadeethAPI.getRawiProfile(rawiId);
      }

      if (rawi) {
          // Headers
          const nameEn = rawi.name_en || rawi.en || 'Transmitter';
          const nameId = rawi.name_id || rawi.id || nameEn;
          const nameAr = rawi.name_ar || rawi.ar || '';
          
          if(document.getElementById('profile-english-name')) document.getElementById('profile-english-name').innerText = nameEn;
          if(document.getElementById('profile-header-name-en')) document.getElementById('profile-header-name-en').innerText = nameEn;
          if(document.getElementById('profile-header-name-id')) document.getElementById('profile-header-name-id').innerText = nameId;
          if(document.getElementById('profile-arabic-name')) document.getElementById('profile-arabic-name').innerText = nameAr;
          if(document.getElementById('profile-nasab')) document.getElementById('profile-nasab').innerText = `Nasab: ${rawi.nasab || nameEn}`;
          
          // Stats
          if(document.getElementById('profile-grade-badge')) document.getElementById('profile-grade-badge').innerText = `Grade: ${rawi.grade || 'Unknown'}`;
          if(document.getElementById('profile-header-grade')) document.getElementById('profile-header-grade').innerText = rawi.grade || 'Unknown';
          
          // Quick Info
          if(document.getElementById('profile-kunyah')) document.getElementById('profile-kunyah').innerText = rawi.kunyah || rawi.kunya_en || 'N/A';
          if(document.getElementById('profile-settled')) document.getElementById('profile-settled').innerText = rawi.city_of_death || rawi.residence || 'Hijaz';
          
          let dates = rawi.dates || '';
          if (!dates && rawi.died_ah) dates = `${rawi.died_ah} AH / ${rawi.died_ce} CE`;
          if(document.getElementById('profile-dates')) document.getElementById('profile-dates').innerText = dates || 'N/A';
          if(document.getElementById('profile-parents')) document.getElementById('profile-parents').innerText = rawi.parents || 'N/A';
      }
  }
  
  // Call it when DOM is ready
  document.addEventListener('DOMContentLoaded', () => {
      setTimeout(renderProfileData, 100);
  });
</script>
</body>"""
    detail_html = detail_html.replace('</body>', inject_script)
    with open('profile-detail.html', 'w', encoding='utf-8') as f:
        f.write(detail_html)
    print("Injected rendering logic into profile-detail.html")
