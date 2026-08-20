import json
with open(r'C:\Users\waverider\.gemini\antigravity\brain\b68056e9-e3e4-4fb4-b8ab-a847328a1abd\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f, open('temp_out.txt', 'w', encoding='utf-8') as out:
    for line in f:
        obj = json.loads(line)
        if obj.get('type') == 'USER_INPUT':
            out.write(f"Step {obj.get('step_index')}:\n")
            out.write(obj.get('content')[:1000] + "\n")
            out.write('-'*50 + "\n")
