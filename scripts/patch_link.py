with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace: const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? (linkGraph.fawaz_to_ab[fawazId] || null) : null);
app_js = app_js.replace("const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? (linkGraph.fawaz_to_ab[fawazId] || null) : null);", 
                        "const abId = activeDataset === 'native_ahmedbaset' ? hadithId : (linkGraph.fawaz_to_ab ? linkGraph.fawaz_to_ab[fawazId] : (linkGraph[fawazId] ? linkGraph[fawazId].ahmedbaset_id : null));")

# Also patch the hadith-list.js or hadith.js equivalent if it's there
app_js = app_js.replace("targetAbId = linkGraph.fawaz_to_ab[num];",
                        "targetAbId = linkGraph.fawaz_to_ab ? linkGraph.fawaz_to_ab[num] : (linkGraph[num] ? linkGraph[num].ahmedbaset_id : null);")

app_js = app_js.replace("if (linkGraph && linkGraph.fawaz_to_ab && linkGraph.fawaz_to_ab[num])",
                        "if (linkGraph && ((linkGraph.fawaz_to_ab && linkGraph.fawaz_to_ab[num]) || (linkGraph[num] && linkGraph[num].ahmedbaset_id)))")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched linkGraph usages.")
