import json
with open("../data/api/muslim.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj['id'] == 2645:
            with open("test_2645.txt", "w", encoding="utf-8") as out:
                out.write("AR:\n" + obj['translations']['ar'][0]['text'] + "\n\n")
                out.write("EN:\n" + obj['translations']['en'][0]['text'] + "\n")
            break