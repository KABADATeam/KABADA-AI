import numpy as np
from copy import deepcopy


class Beam:
    cnt = 0

    def __init__(self, *triple):
        node, val, self.prob = triple
        self.vals = [(node, val, self.prob)]
        self.probs_history = [self.prob]
        self.id = Beam.cnt
        Beam.cnt += 1

    def update_probs(self, bn_net):
        for node, *_ in self.vals:
            bn_net.net.clear_evidence(node)

        self.probs_history.clear()
        for node, val, _ in self.vals:
            if not bn_net.net.is_value_valid(node):
                bn_net.net.update_beliefs()
            self.probs_history.append(bn_net.net.get_node_value(node)[val])
            bn_net.add_evidence(node, val)

        # probs = np.asarray(self.probs_history)
        # self.prob = 1 - np.prod((1 - probs))

    def add_element(self, *triple):
        node, val, prob = triple
        self.vals.append((node, val, prob))
        self.probs_history.append(prob)

        # probs = np.asarray(self.probs_history)
        # self.prob = 1 - np.prod((1 - probs))
        self.prob = np.average(self.probs_history)

    def add_element_by_generating_new(self, *triple):
        new_beam = deepcopy(self)
        new_beam.id = Beam.cnt
        Beam.cnt += 1
        new_beam.add_element(*triple)
        return new_beam

    def __repr__(self):
        return str(self.vals) + " " + str(self.prob)


def beam_search(self, nodes, flag_noisy, num_beams):
    # generating prediction
    beams = []
    for i_node, node in enumerate(nodes):
        if i_node == 0:
            probs = self.get_node_probs(node)
            for val in range(len(probs)):
                beams.append(Beam(node, val, probs[val]))
        else:
            for i_beam in range(len(beams)):
                beam = beams[i_beam]
                beam.update_probs(self)
                probs_net = self.get_node_probs(node)

                for val, prob in enumerate(probs_net):
                    if val == 0:
                        beam.add_element(node, val, prob)
                    else:
                        beams.append(beam.add_element_by_generating_new(node, val, prob))
            probs = [beam.prob for beam in beams]

        if flag_noisy:
            inds = np.random.choice(len(probs), size=min(num_beams, len(probs)), p=probs, replace=False)
        else:
            inds = np.argsort(-np.asarray(probs))[:num_beams]

        for i in list(reversed(range(len(beams)))):
            if i not in inds:
                beams.pop(i)

    # cleaning output
    i_opt = np.argmax([_.prob for _ in beams])
    pairs = [(self.net.get_node_name(node), self.net.get_outcome_id(node, val)) for node, val, prob in beams[i_opt].vals
             if prob >= self.tresh_yes]
    return pairs


if __name__ == "__main__":
    import pysmile
    from BayesNetwork import MultiNetwork
    from config import path_temp_data_file
    mbn = MultiNetwork(tresh_yes=0.0)
    bn = mbn.bns["consumer_segments"]

    for node in [2, 3, 4, 5, 6, 12, 17]:
        bn.net.set_node_type(node, int(pysmile.NodeType.CPT))
        bn.net.update_beliefs()
        n_vals = len(bn.net.get_node_value(node))
        parents = bn.net.get_parents(node)
        print(bn.net.get_node_name(node), [bn.net.get_node_name(node) for node in parents])
        cpt = np.asarray(bn.net.get_node_definition(node)).reshape(-1, n_vals)
    exit()
    for node in bn.net.get_all_nodes():
        print(node, bn.net.get_parents(node), bn.net.get_node_name(node))





