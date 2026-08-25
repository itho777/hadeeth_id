
import os, glob, re

html_files = glob.glob("../*.html")

for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("gap-stack-lg", "gap-8")

    desktop_nav_match = re.search(r'(<nav class="hidden md:flex.*?>.*?</nav>)', content, re.DOTALL)
    if desktop_nav_match:
        nav_content = desktop_nav_match.group(1)
        if "glossary.html" not in nav_content:
            if "admin.html" in nav_content:
                is_active = "glossary.html" in filepath
                if is_active:
                    link = '<a href="glossary.html" data-nav-page="glossary.html" class="text-primary dark:text-white font-bold border-b-2 border-primary dark:border-[#10b981] py-1">Glossary</a>'
                else:
                    link = '<a href="glossary.html" data-nav-page="glossary.html" class="text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white py-1 transition-colors">Glossary</a>'
                
                new_nav_content = re.sub(r'(<a href="admin\.html".*?>.*?</a>)', r'{}' + '\n      \\1', nav_content)
                new_nav_content = new_nav_content.format(link)
                content = content.replace(nav_content, new_nav_content)

    mobile_menu_inner = re.search(r'(<div class="flex flex-col px-margin-main py-2 gap-1">)(.*?)(</div>)', content, re.DOTALL)
    if mobile_menu_inner:
        inner_content = mobile_menu_inner.group(2)
        if "glossary.html" not in inner_content:
            is_active = "glossary.html" in filepath
            if is_active:
                link = '<a href="glossary.html" class="py-2 text-primary dark:text-white font-bold">Glossary</a>'
            else:
                link = '<a href="glossary.html" class="py-2 text-on-surface-variant dark:text-gray-400 hover:text-primary dark:hover:text-white">Glossary</a>'
            
            new_inner = re.sub(r'(<a href="admin\.html".*?>.*?</a>)', r'{}' + '\n      \\1', inner_content)
            new_inner = new_inner.format(link)
            content = content.replace(inner_content, new_inner)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Header fixed in all HTML files.")
