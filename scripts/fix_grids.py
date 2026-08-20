import re
with open('profile-detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Append clear loading logic
inject = """
          // Clear Hadith Grids loading text if we don't have an API to fetch them yet
          if(document.getElementById('transmitted-count-badge')) document.getElementById('transmitted-count-badge').innerText = `${rawi.hadith_count || 0} Total`;
          if(document.getElementById('transmitted-hadiths-grid')) document.getElementById('transmitted-hadiths-grid').innerHTML = `<div class="p-6 text-center text-xs text-outline dark:text-gray-400">Offline dataset active. Detailed narrations list currently unavailable for this specific profile.</div>`;
      }
  }
"""

html = html.replace("      }\n  }\n  \n  // Call it when DOM is ready", inject + "  \n  // Call it when DOM is ready")

with open('profile-detail.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Added hadith grid fallback text")
