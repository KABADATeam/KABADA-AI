import pysmile
import json
from config import repo_dir
from os.path import join
from pprint import pprint
import smile_licence.pysmile_license
import numpy as np
from bs4 import BeautifulSoup
from copy import deepcopy
from collections import Counter

with open(join(repo_dir, "docs", "NACE_data.json"), "rb") as conn:
    nace = json.load(conn)

node_genie_extension = '<node id="nace_A">\
<name>agro_forest_fish</name>' \
'<interior color="e5f6f7" />' \
'<outline color="000080" />' \
'<font color="000000" name="Arial" size="8" />' \
'<position>104 90 301 130</position>' \
'</node>'

defcomment_genie_extension = '<defcomment row="0" col="0">this is annotation</defcomment>'

node_cpt = '<cpt id="nace_A"></cpt>'
state_cpt = '<state id="State1" />'
# '<probabilities>0.5 0.5</probabilities>'
probablities_cpr = '<probabilities></probabilities>'


node_genie_extension = BeautifulSoup(node_genie_extension, 'lxml').node
defcomment_genie_extension = BeautifulSoup(defcomment_genie_extension, 'lxml').defcomment
node_cpt = BeautifulSoup(node_cpt, 'lxml').cpt
state_cpt = BeautifulSoup(state_cpt, 'lxml').state
probablities_cpr = BeautifulSoup(probablities_cpr, 'lxml').probabilities



# print(node_genie_extension)
print(probablities_cpr)


print(len(nace))
list_cpt_nodes = []
counter = Counter()
for c in nace:
    for a in c['activities']:
        counter[len(a['Code'])] += 1
print(counter)
dict_len2lev = {k: i + 1 for i, (k, v) in enumerate(reversed(counter.most_common()))}


dict_cpts = {'lev0': [], 'lev1': [],
             'lev2': [], 'lev3': []
             }

def make_state(name, ann, irow):
    s = deepcopy(state_cpt)
    s1 = deepcopy(defcomment_genie_extension)
    s['id'] = name + " " + ann
    s1['row'] = irow
    s1.string = ann
    return s, s1


for ic, c in enumerate(nace):
    dict_cpts['lev0'].append(make_state(c["Code"], c["Title"], ic))

    for ia, a in enumerate(c['activities']):
        n = deepcopy(node_cpt)
        lev = "lev" + str(dict_len2lev[len(a['Code'])])
        dict_cpts[lev].append(make_state(a['Code'], a['Title'], len(dict_cpts[lev])))
        # if ia > 3:
        #     break

with open(join(repo_dir, "bayesgraphs", "nace_template.xdsl"), "r") as conn:
    nace_bn = BeautifulSoup(conn.read(), 'lxml').smile

prev_lev = None
for lev in ['lev1', 'lev0']:
    vs = dict_cpts[lev]
    n = deepcopy(node_cpt)
    n['id'] = "nace_" + lev

    e = deepcopy(node_genie_extension)
    e['id'] = "nace_" + lev
    e.find('name').string = "nace_" + lev

    for cpt, ext in vs:
        n.append(cpt)
        e.append(ext)

    if prev_lev is not None:
        probs = np.zeros((len(dict_cpts[prev_lev]), len(dict_cpts[lev])))

        for iprev, (xml, _) in enumerate(dict_cpts[prev_lev]):
            for i, (xml1, _) in enumerate(dict_cpts[lev]):
                probs[iprev, i] = 1 if xml1['id'] in xml['id'] else 0
                # probs[iprev, i] = iprev
        # print(np.sum(probs, 1))

        # probs = (probs.T / np.sum(probs, 1)).T
        # probs = (probs / np.sum(probs, 0)).T
        print("np.sum(probs)", np.sum(probs))

        probs1 = deepcopy(probablities_cpr)
        probs1.string = " ".join(map(str, probs.flatten()))

        p = BeautifulSoup(f"<parents>{'nace_' + prev_lev}</parents>", 'lxml').find('parents')
        n.append(p)
        # p = BeautifulSoup(f"<parents>{lev}</parents>", 'lxml').find('parents')
        # nace_bn.find_all("node")[-1].append(p)
    else:
        probs1 = deepcopy(probablities_cpr)
        probs1.string = " ".join(map(str, [1 / len(vs)] * len(vs)))

    n.append(probs1)
    nace_bn.nodes.append(n)
    nace_bn.extensions.genie.append(e)

    prev_lev = lev
    # if lev == "lev1":
    #     break

with open(join(repo_dir, "bayesgraphs", "nace.xdsl"), "w") as conn:
    conn.write(str(nace_bn))
# pprint(dict_cpts['lev0'])