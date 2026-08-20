import re
text = open('js/app.js', encoding='utf-8').read()
text = text.replace("renderDatasetBanner('dataset-banner-list');", "renderDatasetBanner(bookId, 'dataset-banner-list', datasetParam);")
text = text.replace("renderDatasetBanner('dataset-banner');", "renderDatasetBanner(bookId, 'dataset-banner');")
open('js/app.js', 'w', encoding='utf-8').write(text)
