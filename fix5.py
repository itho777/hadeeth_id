
text = open('js/app.js', encoding='utf-8').read()
text = text.replace('async =>', 'async () =>')
open('js/app.js', 'w', encoding='utf-8').write(text)

