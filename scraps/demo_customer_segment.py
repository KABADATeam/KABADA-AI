import numpy as np
import pysmile

# pysmile_license is your license key
import smile_licence.pysmile_license
import pandas as pd
from pprint import pprint

class BayesNetwork:
    def __init__(self):
        self.net = pysmile.Network()
        self.net.read_file("kabada_customer_segments.xdsl")
        self.num_added_evidence = 0
        # pprint([_ for _ in dir(self.net) if "get_" in _])
        # # print(self.net.get_first_node())
        # # exit()
        # print(self.net.get_all_node_ids())
        # print(self.net.get_all_nodes())
        # # exit()
        # self.id2name = {k: v for k, v in zip(self.net.get_all_node_ids(), self.net.get_all_nodes())}
        # # pprint(self.id2name)
        # # exit()

    def learn(self, path_newdata):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()
        em.learn(ds, self.net, matching)

    def add_evidence(self, varname, val):
        self.num_added_evidence += 1
        self.net.set_evidence(varname, val)
        self.net.update_beliefs()

    def predict_popup(self, varname):
        if self.num_added_evidence == 0:
            arr = self.net.get_node_definition(varname)
            # self.net.get_node_count(self.net.get_node(varname))
            # node = self.net.get_node(varname)
            # print(node)
            n = len(arr)
            n2 = int(n / 2) # number of states are 2
            arr = np.array([arr[:n2], arr[n2:]])
            print("add some evidence")
            return None
        probs = self.net.get_node_value(varname)
        i_most_likely = np.argmax(probs)
        return self.net.get_outcome_id(varname, i_most_likely), probs[i_most_likely]

    def clear_evidence(self, varname=None):
        if varname is None:
            self.num_added_evidence = 0
            self.net.clear_all_evidence()
        else:
            self.num_added_evidence -= 1
            self.net.clear_evidence(varname)


popup_ai = BayesNetwork()

# tab = pd.read_csv("kabada_customer_segments.txt")
# print(tab.columns)
# exit()
# popup_ai.add_evidence("is_added_consumer", "no")
popup_ai.add_evidence("age_under_12", "yes")
popup_ai.add_evidence("age_12_17", "no")
popup_ai.add_evidence("age_18_24", "no")
popup_ai.add_evidence("age_25_34", "no")
popup_ai.add_evidence("age_35_64", "no")
popup_ai.add_evidence("age_65_74", "no")
popup_ai.add_evidence("age_75_over", "no")
print(popup_ai.predict_popup("education_primary"))
print(popup_ai.predict_popup("education_secondary"))
print(popup_ai.predict_popup("education_higher"))

