import numpy as np
import pysmile
from pprint import pprint

# pysmile_license is your license key
import smile_licence.pysmile_license

class BayesNetwork:
    def __init__(self, path="../bayesgraphs/business_plan.xdsl"):
        self.net = pysmile.Network()
        self.net.read_file(path)

    def learn(self, path_newdata):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()
        em.learn(ds, self.net, matching)

    def add_evidence(self, varname, val):
        self.net.set_evidence(varname, val)
        self.net.update_beliefs()

    def predict_popup(self, varname):
        probs = self.net.get_node_value(varname)
        i_most_likely = np.argmax(probs)
        return self.net.get_outcome_id(varname, i_most_likely), probs[i_most_likely]

    def clear_evidence(self, varname=None):
        if varname is None:
            self.net.clear_all_evidence()
        else:
            self.net.clear_evidence(varname)


def learn_net_from_scratch():
    ds = pysmile.learning.DataSet()
    ds.read_file("../bayesgraphs/business_plan.txt")
    search = pysmile.learning.BayesianSearch()
    # search = pysmile.learning.TAN()
    net = search.learn(ds)
    # net.add_node(pysmile.NodeType.NOISY_MAX, "ccccc")
    print([net.get_node_name(_) for _ in net.get_all_nodes()])
    # net.add_arc("telpas", 'ienakumu_veids')

    # pprint(dir(net))
    net.write_file("../bayesgraphs/trained_graphs/business_plan_bayes_searched.xdsl")
    return net


net = BayesNetwork()
net_nm = BayesNetwork("../bayesgraphs/business_plan_with_noisy_max.xdsl")

for node in net.net.get_all_nodes():
    node_name = net.net.get_node_name(node)

    print(1111111, net_nm.net.get_node_type(node) == pysmile.NodeType.NOISY_MAX)
    net_nm.net.set_node_type(node, pysmile.NodeType.CPT)
    print(node_name, net.net.get_node_type(node_name), net_nm.net.get_node_type(node_name))

    v = net.net.get_node_definition(node_name)
    v_nm = net_nm.net.get_node_definition(node_name)
    print(len(v), v)
    print(len(v_nm), v_nm)

net_nm.learn("../bayesgraphs/business_plan.txt")

exit()

# up
popup_ai = BayesNetwork()



# exit()

# net2 = learn_net_from_scratch()
# net2 = BayesNetwork("../bayesgraphs/trained_graphs/business_plan_bayes_searched.xdsl")
net2 = popup_ai


for node in net2.net.get_all_nodes():
    node_name = net2.net.get_node_name(node)
    print(node_name, net2.net.get_node_definition(node_name))
    # exit()
    # exit()


exit()
popup_ai.net = net

# print(popup_ai)
# # pysmile.learning.GreedyThickThinning("../bayesgraphs/business_plan.txt")
# exit()

# Janis ievada, ka darbosies IT nozaree
popup_ai.add_evidence("nozare", "IT")

# Janis ievada, ka stradas ofisa
print("piedavātā telpu vērtība: ", popup_ai.predict_popup("telpas"))
popup_ai.add_evidence("telpas", "ofiss")

# Janis ievada, ka klienti bus biznesi
print("piedavātā klientu vērtība: ", popup_ai.predict_popup("klienti"))
popup_ai.add_evidence("klienti", "uznemumi")

# Janis ievada ienakumu veidu
print("piedavātie ienākumu veidi: ", popup_ai.predict_popup("ienakumu_veids"))
popup_ai.add_evidence("ienakumu_veids", "regulari_pirkumi")

# Janis ievada finansejuma veidu
print("piedavātie finansejuma veidi: ", popup_ai.predict_popup("finansesana"))
popup_ai.add_evidence("finansesana", "investori")

# Janis ievada cash flow
print("piedavātās cash flow scenariji: ", popup_ai.predict_popup("cash_flow"))
popup_ai.add_evidence("cash_flow", "pozitivs_pec_3_gadiem")
