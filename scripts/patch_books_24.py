with open('books.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Skeleton
html = html.replace("Array(8).fill('').map(makeSkeletonCard).join('');", "Array(15).fill('').map(makeSkeletonCard).join('');")

# 2. Update Map slice
html = html.replace("secondaryGrid.innerHTML = data.slice(9,17).map(makeCard).join('');", "secondaryGrid.innerHTML = data.slice(9).map(makeCard).join('');")

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched books.html to display all 24 kitabs!")
