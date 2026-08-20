import re

text = open('js/app.js', encoding='utf-8').read()
text = text.replace("let activeDsLabelId = 'Edisi Fawazahmed0';", "let activeDsLabelId = 'Penomoran Internasional';")
text = text.replace("activeDsLabel = 'Fawazahmed0 Edition';", "activeDsLabel = 'International Numbering';")

text = text.replace("activeDsLabelId = 'Edisi Lidwa';", "activeDsLabelId = 'Penomoran Lidwa';")
text = text.replace("activeDsLabel = 'Lidwa Edition';", "activeDsLabel = 'Lidwa Numbering';")

open('js/app.js', 'w', encoding='utf-8').write(text)
