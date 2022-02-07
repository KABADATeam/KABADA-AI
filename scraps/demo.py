import numpy as np
import pysmile

# pysmile_license is your license key
import smile_licence.pysmile_license

class BayesNetwork:
    def __init__(self):
        self.net = pysmile.Network()
        self.net.read_file("bayesgraphs/business_plan.xdsl")

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


popup_ai = BayesNetwork()

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
