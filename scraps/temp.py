import json
from pprint import pprint
from collections import Counter
from re import findall

with open("../docs/Texter.txt", "r", encoding="cp866") as conn:
    # codes = json.load(conn)
    codes = conn.read().split("\n")

counter = Counter()

for code in codes:
    a = findall(r"\"Id\":\"(.*)\",\"Value\":\"(.*)\",\"Kind\"([0-9]*)", code)
    if len(a) == 0:
        continue
    guid, value, kind = a[0]
    counter[value] += 1


print(counter.most_common(20))
