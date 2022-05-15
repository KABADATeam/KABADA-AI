import pandas as pd
from config import path_temp_data_file
from collections import Counter

tab = pd.read_csv(path_temp_data_file, sep=" ")

print(tab.shape)
print(tab.columns)
for c in tab.columns:
    counter = Counter(tab[c])
    print(c, counter, len(counter))