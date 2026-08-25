import json

with open("../data/raw_baseline/ara-muslim.json", "r") as f:
    ara_data = json.load(f)
ara_nums = [str(h.get('hadithnumber', h.get('id'))) for h in ara_data['hadiths']]

with open("../data/raw_baseline/eng-muslim.json", "r") as f:
    eng_data = json.load(f)
eng_nums = [str(h.get('hadithnumber', h.get('id'))) for h in eng_data['hadiths']]

print("Ara total: " + str(len(ara_nums)))
print("Eng total: " + str(len(eng_nums)))

ara_set = set(ara_nums)
eng_set = set(eng_nums)

missing_in_eng = ara_set - eng_set
missing_in_ara = eng_set - ara_set

print("Missing in Eng: " + str(len(missing_in_eng)))
if len(missing_in_eng) > 0:
    nums = sorted([int(x) for x in missing_in_eng if str(x).isdigit()])
    ranges = []
    if nums:
        start = nums[0]
        prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            else:
                if start == prev:
                    ranges.append(str(start))
                else:
                    ranges.append(str(start) + "-" + str(prev))
                start = n
                prev = n
        if start == prev:
            ranges.append(str(start))
        else:
            ranges.append(str(start) + "-" + str(prev))
    print("Missing in Eng ranges: " + ", ".join(ranges))

print("Missing in Ara: " + str(len(missing_in_ara)))