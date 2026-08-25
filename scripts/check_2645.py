import json
with open("../data/api/muslim.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        if obj['id'] == 2645:
            print("Lidwa AR:", obj['translations']['ar'][0]['text'][:200].encode('ascii', 'ignore').decode('ascii'))
            print("Lidwa IDO:", obj['translations']['id'][0]['text'][:200].encode('ascii', 'ignore').decode('ascii'))
            if 'en' in obj['translations']:
                print("Fawaz EN:", obj['translations']['en'][0]['text'][:200].encode('ascii', 'ignore').decode('ascii'))
            break