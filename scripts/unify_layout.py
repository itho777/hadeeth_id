import glob
import re

def main():
    # Read index.html for canonical header and footer
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    header_match = re.search(r'<header.*?</header>', content, re.DOTALL)
    footer_match = re.search(r'<footer.*?</footer>', content, re.DOTALL)
    
    if not header_match or not footer_match:
        print("Could not find header or footer in index.html")
        return
        
    base_header = header_match.group(0)
    base_footer = footer_match.group(0)
    
    # Fix duplicate data-i18n in base header
    base_header = re.sub(r'(data-i18n="[^"]+")\s+(class="[^"]+")\s+\1', r'\1 \2', base_header)
    
    active_mapping = {
        'books.html': 'books.html',
        'books2.html': 'books.html',
        'kitab.html': 'books.html',
        'hadith.html': 'books.html',
        'hadith-list.html': 'books.html',
        'topics.html': 'topics.html',
        'topics-in-kitab.html': 'topics.html',
        'topic-hadiths.html': 'topics.html',
        'scholars.html': 'scholars.html',
        'profile-detail.html': 'scholars.html',
        'sanad.html': 'scholars.html',
        'admin.html': 'admin.html'
    }
    
    # CSS Classes
    desktop_inactive = 'text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors'
    desktop_active = 'text-primary dark:text-white font-bold border-b-2 border-primary dark:border-[#10b981] py-1'
    
    mobile_inactive = 'py-2 text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white'
    mobile_active = 'py-2 text-primary dark:text-white font-bold'
    
    html_files = glob.glob('*.html')
    
    for f in html_files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Customize header for this file
        current_header = base_header
        active_target = active_mapping.get(f)
        
        if active_target:
            # Replace desktop link classes
            desktop_regex = r'(<a\s+href="'+active_target+r'".*?class=")([^"]+)(".*?>)'
            current_header = re.sub(desktop_regex, lambda m: m.group(1) + desktop_active + m.group(3) if desktop_inactive in m.group(2) else m.group(0), current_header)
            
            # Replace mobile link classes (they are inside <div id="mobile-menu">)
            mobile_regex = r'(<div id="mobile-menu".*?<a\s+href="'+active_target+r'"\s+class=")([^"]+)(".*?>)'
            current_header = re.sub(mobile_regex, lambda m: m.group(1) + mobile_active + m.group(3) if 'text-on-surface' in m.group(2) else m.group(0), current_header, flags=re.DOTALL)
            
        # Strip old header/nav and footer
        # We replace <header>...</header> or <nav>...</nav> (if it's the main nav)
        content = re.sub(r'<header.*?</header>', current_header, content, flags=re.DOTALL)
        
        if '<header' not in content:
            # Try to replace <nav> if it was used as root
            content = re.sub(r'<nav[^>]*>.*?</nav>', current_header, content, count=1, flags=re.DOTALL)
            
        # Replace footer
        content = re.sub(r'<footer.*?</footer>', base_footer, content, flags=re.DOTALL)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Updated {f}")

if __name__ == '__main__':
    main()
