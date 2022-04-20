import pickle
from Translator import Flattener
from BayesNetwork import MultiNetwork

with open("../bp.pickle", "rb") as conn:
    bp = pickle.load(conn)

mbn = MultiNetwork()
flattener = Flattener()

guids_by_bn = flattener(bp, flag_generate_plus_one=True)

recomendations_by_bn = mbn.predict_all(guids_by_bn)

bp = flattener.back(recomendations_by_bn)
