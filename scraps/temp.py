import json
from pprint import pprint
from collections import Counter
from re import findall
from collections import defaultdict
from Translator import Flattener, Translator

with open("../docs/Texter.txt", "r", encoding="cp866") as conn:
    # codes = json.load(conn)
    codes = conn.read().split("\n")

def check_value_counts():
    counter = Counter()
    for code in codes:
        a = findall(r"\"Id\":\"(.*)\",\"Value\":\"(.*)\",\"Kind\"([0-9]*)", code)
        if len(a) == 0:
            continue
        guid, value, kind = a[0]
        counter[value] += 1
    print(counter.most_common(20))


def print_kind_associated_guids(kind0):
    vals = []
    guids = []
    for code in codes:
        a = findall(r"\"Id\":\"(.*)\",\"Value\":\"(.*)\",\"Kind\":([0-9]*)", code)
        if len(a) == 0:
            continue
        guid, value, kind = a[0]
        if int(kind) == int(kind0):
            guids.append('"' + guid + '"')
            vals.append((guid, value))
    print(", ".join(guids))
    pprint(vals)


def print_value2kind(value0):
    kinds = []
    for code in codes:
        a = findall(r"\"Id\":\"(.*)\",\"Value\":\"(.*)\",\"Kind\":([0-9]*)", code)
        if len(a) == 0:
            continue
        guid, value, kind = a[0]
        if value == value0:
            kinds.append(kind)
    print(kinds)


def print_probable_flat_guids():
    flattener = Flattener()
    translator = Translator()

    all_new_guids = defaultdict(list)
    for a in flattener(flattener.full_bp):
        print(a)
        all_new_guids[a.split("::")[-1]].append(a)

    # for guid, translation in translator.lookup.items():
    #     if len(all_new_guids[guid]) > 1:
    #         print(translation, all_new_guids[guid])
    #         exit()
    # print(translator.lookup.keys())


if __name__ == "__main__":
    # check_value_counts()
    # print_kind_associated_guids(38)
    # print_value2kind("Manufacturing")
    print_probable_flat_guids()