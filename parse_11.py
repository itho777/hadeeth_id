import json

batch_path = r"C:\Users\waverider\.gemini\antigravity\brain\a8b4a1aa-b3d0-485e-90c7-42c1496cd802\scratch\batch_11.json"

with open(batch_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total items in batch_11: {len(data)}")

for i, item in enumerate(data):
    print(f"Index {i}: ID={item['id']}, Targets={item.get('targets', [])}")
