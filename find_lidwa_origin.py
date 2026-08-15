import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'C:\Users\waverider\.gemini\antigravity\brain\904c8a72-b9f4-4d32-a304-6473f61666ae\.system_generated\logs\transcript.jsonl'
try:
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'irsyadulibad' in line.lower() or 'lidwa' in line.lower() or 'clone' in line.lower():
                data = json.loads(line)
                if data['type'] in ('USER_INPUT', 'PLANNER_RESPONSE') or 'tool_calls' in data:
                    print(f"--- {data['type']} ---")
                    if 'content' in data:
                        print(data['content'][:200])
                    if 'tool_calls' in data:
                        for call in data['tool_calls']:
                            print(call.get('name'), str(call.get('arguments'))[:150])
except Exception as e:
    print('Error:', e)
