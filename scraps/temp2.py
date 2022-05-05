import pandas as pd
from sklearn.metrics import confusion_matrix
from collections import Counter
import pickle

tab = pd.read_csv(f"../bayesgraphs/main.txt", sep=" ")
tab1 = pd.read_csv(f"../bayesgraphs/main1.txt", sep=" ")

varname = 'nace'
counter = Counter(tab[varname])
print(confusion_matrix(tab[varname], tab1[varname], labels=[_[0] for _ in counter.most_common()]))

# with open("../tests/temp.pickle", "rb") as conn:
#     sampled, exp = pickle.load(conn)
#
# print(confusion_matrix(exp, sampled))