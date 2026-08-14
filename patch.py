with open('hadith.html', 'r', encoding='utf-8') as f:
    text = f.read()

logger = '''
<div id="debug-log" style="position:fixed;bottom:0;left:0;right:0;height:200px;background:rgba(0,0,0,0.8);color:#0f0;overflow:auto;z-index:9999;font-family:monospace;padding:10px;">Debug Log:</div>
<script>
window.onerror = function(msg, url, line) {
    document.getElementById("debug-log").innerHTML += "<br><span style=\\"color:red\\">ERR: " + msg + " at " + line + "</span>";
};
window.onunhandledrejection = function(e) {
    document.getElementById("debug-log").innerHTML += "<br><span style=\\"color:red\\">REJ: " + (e.reason && e.reason.message ? e.reason.message : e.reason) + "</span>";
};
</script>
'''
if 'id="debug-log"' not in text:
    text = text.replace('</body>', logger + '</body>')
    with open('hadith.html', 'w', encoding='utf-8') as f:
        f.write(text)
