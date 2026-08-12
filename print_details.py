import json

batch_path = r"C:\Users\waverider\.gemini\antigravity\brain\a8b4a1aa-b3d0-485e-90c7-42c1496cd802\scratch\batch_11.json"

with open(batch_path, "r", encoding="utf-8") as f:
    data = json.load(f)

with open("batch_11_dump.txt", "w", encoding="utf-8") as out:
    for i, item in enumerate(data):
        out.write(f"=== [{i}] ID: {item['id']} ===\n")
        out.write(f"TARGETS: {item.get('targets')}\n")
        out.write(f"ARABIC:\n{item['arabic']}\n")
        out.write(f"INDONESIAN:\n{item['indonesian_snippet']}\n")
        out.write("-" * 50 + "\n")

print("Successfully written to batch_11_dump.txt")
