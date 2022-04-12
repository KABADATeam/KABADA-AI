import numpy as np
import pysmile
from os.path import join
from collections import defaultdict
import smile_licence.pysmile_license
from BayesNetwork import BayesNetwork
from config import net_dir
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint

# bn = BayesNetwork(join(net_dir, "consumer_segments.xdsl"))

def just_generate(name="age_vs_edu"):
    bn = BayesNetwork(join(net_dir, name + ".xdsl"))
    B = 1000
    tab = defaultdict(list)
    for i in range(B):
        # print(bn.generate_one_sample())
        # exit()
        for colname, colval in bn.generate_one_sample():
            tab[colname].append(colval)
        # exit()
        for k in tab.keys():
            if len(tab[k]) < i + 1:
                tab[k].extend(['no'] * (i + 1 - len(tab[k])))

    tab = pd.DataFrame(tab)
    tab.to_csv("../bayesgraphs/consumer_segments2.txt", sep=" ", index=False)
    print(tab.shape)


def education_vs_education():
    just_generate('consumer_segments')
    tab = pd.read_csv("../bayesgraphs/consumer_segments2.txt", sep=" ")

    # edus = ['education_primary', 'education_secondary', 'education_higher']
    edus = sorted(tab.columns)

    freqs = []
    for age in edus:
        freqs.append(np.average(tab[age] == 'yes'))
    print(edus)
    print(freqs, 1 / len(edus))
    exit()


def age_vs_education():
    # just_generate()
    just_generate('consumer_segments')
    tab = pd.read_csv("../bayesgraphs/consumer_segments2.txt", sep=" ")

    ages = ['age_under_12', 'age_12_17', 'age_18_24', 'age_25_34', 'age_35_64', 'age_65_74', 'age_75_over']
    edus = ['education_primary', 'education_secondary', 'education_higher']

    # freqs = []
    # for age in ages:
    #     freqs.append(np.average(tab[age] == 'yes'))
    # print(freqs, 1 / len(ages))
    # exit()

    img = np.zeros((len(ages), len(edus)))
    for i, age in enumerate(ages):
        for j, edu in enumerate(edus):
            img[i, j] = np.sum(np.logical_and(tab[age] == 'yes', tab[edu] == 'yes'))# / np.sum(tab[age] == 'yes')

    img = (img.T / np.sum(img, 1)).T
    print(img)
    # plt.imshow(img)
    # plt.show()


def node_vs_node():
    just_generate("noisy_or_test")
    tab = pd.read_csv("../bayesgraphs/consumer_segments2.txt", sep=" ")

    # tab = pd.read_csv("../bayesgraphs/age_vs_edu.txt", sep=" ")
    ages = ["Node4", "Node5"]
    edus = ["Node6"]

    # tab = tab[["Node4", "Node5", "Node6"]]
    # for k in tab.columns:
    #     tab[k] = tab[k].apply(lambda x: 1 if x == "yes" else 0)
    # tab = np.asarray(tab)
    # print(np.corrcoef(tab.T))
    # exit()

    # freqs = []
    # for age in ages:
    #     freqs.append(np.average(tab[age] == 'yes'))
    # print(freqs, 1 / len(ages))
    # exit()

    img = np.zeros((len(ages), len(edus)))
    for i, age in enumerate(ages):
        for j, edu in enumerate(edus):
            img[i, j] = np.average(np.logical_and(tab[age] == 'yes', tab[edu] == 'yes'))  # / np.sum(tab[age] == 'yes')

    # img = (img.T / np.sum(img, 1)).T
    print(img)


age_vs_education()
# node_vs_node()
# education_vs_education()