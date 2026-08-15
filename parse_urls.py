import re
with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\lib.min.js', 'r', encoding='utf-8') as f:
    text = f.read()
    
    urls = re.findall(r'(https?://[^\s\'\"]+)', text)
    apis = re.findall(r'(/api/[^\s\'\"]+)', text)
    print('URLs:', set(urls))
    print('APIs:', set(apis))
    
    jsons = re.findall(r'([a-zA-Z0-9_\-\./]+\.json)', text)
    print('JSONs:', set(jsons))
