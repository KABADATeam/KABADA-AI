from pprint import pprint
from BayesNetwork import MultiNetwork
import numpy as np
from config import path_forbidden_combinations
import json
from collections import defaultdict

mnet = MultiNetwork()

# mnet.bns['main'].add_evidence('consumer_prices', 'fixed_pricing')

pairs = mnet.bns['main'].predict_popup(
    # list_evidence=[('consumer_prices', 'fixed_pricing')],
    # list_evidence=[('consumer_prices', 'dynamic_pricing')],
    targets={'consumer_types_of_pricing'}
)


pprint(pairs)
exit()

net = mnet.bns['main']
for node in net.get_node_iterator():
    print(net.net.get_node_name(node), net.net.get_parents(node))

    n_vals = net.net.get_outcome_count(node)
    cpt = np.asarray(net.net.get_node_definition(node)).reshape(-1, n_vals)
    print(cpt)
    exit()


