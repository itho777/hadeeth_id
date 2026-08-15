import sys
import re

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "label: 'Darussalam / fawazahmed0', labelId: 'Darussalam / fawazahmed0',",
    "label: 'Fawazahmed0 Edition', labelId: 'Edisi Fawazahmed0',"
)
text = text.replace(
    "label: 'AhmedBaset', labelId: 'AhmedBaset',",
    "label: 'AhmedBaset Edition', labelId: 'Edisi AhmedBaset',"
)
text = text.replace(
    "label: 'Lidwa / Irsyad', labelId: 'Lidwa / Irsyad',",
    "label: 'Lidwa Edition', labelId: 'Edisi Lidwa',"
)

text = text.replace("dataset_version') || 'primary'", "dataset_version') || 'fawazahmed'")
text = text.replace("id: 'primary'", "id: 'fawazahmed'")
text = text.replace("=== 'primary'", "=== 'fawazahmed'")
text = text.replace("datasetInfo: { primary:", "datasetInfo: { fawazahmed:")
text = text.replace("datasetInfo || {}).primary", "datasetInfo || {}).fawazahmed")
text = text.replace("const isPrimary = activeDataset === 'primary';", "const isPrimary = activeDataset === 'fawazahmed';")

# Also fix the title to append the edition name in hadithDetail
# Look for: bcCurrentEn.innerText = titleTextEn;
replacement_title = """
  // Append active dataset to title
  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';
  let activeDsLabel = '';
  if (activeDataset === 'native_lidwa') activeDsLabel = 'Lidwa Edition';
  else if (activeDataset === 'native_ahmedbaset') activeDsLabel = 'AhmedBaset Edition';
  else activeDsLabel = 'Fawazahmed0 Edition';

  let activeDsLabelId = '';
  if (activeDataset === 'native_lidwa') activeDsLabelId = 'Edisi Lidwa';
  else if (activeDataset === 'native_ahmedbaset') activeDsLabelId = 'Edisi AhmedBaset';
  else activeDsLabelId = 'Edisi Fawazahmed0';

  if (bcCurrentEn) bcCurrentEn.innerText = titleTextEn + ` (${activeDsLabel})`;
  if (bcCurrentId) bcCurrentId.innerText = titleTextId + ` (${activeDsLabelId})`;
  document.title = `${bookName} Hadith #${hadithId} (${activeDsLabel}) - HADEETH.ID`;
"""
text = text.replace(
    "if (bcCurrentEn) bcCurrentEn.innerText = titleTextEn;\n  if (bcCurrentId) bcCurrentId.innerText = titleTextId;",
    replacement_title
)

with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Phase 1 complete')
