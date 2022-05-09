import numpy as np
from copy import deepcopy
from config import epsilon


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


def beam_search(self, nodes, flag_noisy, num_beams, flag_return_all_beams=False):
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
            probs = np.array([beam.prob for beam in beams])

        if flag_noisy:
            probs /= np.sum(probs)
            probs[probs == 0.0] = 0.01
            probs /= np.sum(probs)
            inds = np.random.choice(len(probs), size=min(num_beams, len(probs)), p=probs, replace=False)
        else:
            inds = np.argsort(-np.asarray(probs))[:num_beams]

        for i in list(reversed(range(len(beams)))):
            if i not in inds:
                beams.pop(i)

    if flag_return_all_beams:
        beam_pairs = []
        for beam in beams:
            beam_pairs.append([
                (self.net.get_node_name(node), self.net.get_outcome_id(node, val))
                for node, val, prob in beam.vals if prob >= self.tresh_yes])
        return beam_pairs

    # cleaning output
    i_opt = np.argmax([_.prob for _ in beams])
    pairs = [(self.net.get_node_name(node), self.net.get_outcome_id(node, val)) for node, val, prob in beams[i_opt].vals
             if prob >= self.tresh_yes]
    return pairs


if __name__ == "__main__":
    from pprint import pprint
    from BayesNetwork import MultiNetwork
    from itertools import combinations
    from config import path_temp_data_file
    mbn = MultiNetwork(tresh_yes=0.0)
    bn = mbn.bns["consumer_segments"]
    # bn = mbn.bns["fixed_costs"]

    beams = bn.predict_popup(num_beams=30, flag_with_nos=True, flag_return_all_beams=True)
    varnames = sorted([_[0] for _ in beams[0]])

    values = []
    for beam in beams:
        beam = {k: v for k, v in beam}
        values.append("::".join([beam[k] for k in varnames]))
    print(len(values), len(set(values)))
    i0, i1 = 1, 2
    for i0, i1 in combinations(range(len(beams)), 2):

        beam0 = [(a, 'no') for a, b in beams[i0]]
        beam1 = [(a, 'yes') for a, b in beams[i1]]
        # beam0 = beams[i0]
        # beam1 = beams[i1]

        dist = bn.distance(beam0, beam1, flag_simple_dist=False)
        print(i0, i1, dist)
        exit()



