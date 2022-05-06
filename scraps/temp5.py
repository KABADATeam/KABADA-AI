import pickle
from pprint import pprint
from re import findall
from BayesNetwork import MultiNetwork
from Translator import Flattener, Translator
import json

# translator = Translator()
# prefix = "plan::costs::fixedCosts::category::"
# # prefix = "plan::costs::fixedCosts::subCategory::"
# guids = []
# for guid in translator.lookup.keys():
#     if prefix in guid:
#         guids.append(guid.replace(prefix, ""))
# print(str(guids).replace("'", '"'))
# exit()

with open("../stout.pickle", "rb") as conn:
    bp = pickle.load(conn)

# with open("../bp.pickle", "rb") as conn:
#     bp = pickle.load(conn)


# pprint(bp)
# exit()
with open("../stout.json", "w") as conn:
    json.dump(bp, conn)

# ss = {"25feae02-736b-44c7-b6e7-06fa502f4c63", "3c36a2c7-4cd3-43b1-98f5-270c8c98edd7", "3943c265-621b-4738-93c8-4470986c3af3", "7682545b-fbee-475e-ab30-5a1f694c81c6", "e2d723ce-1ea6-4d1e-a35e-5b47907d2d2a", "aa351db4-3b28-4cab-ad95-722bfcba23dc", "4b0ba05e-88c6-4c54-a313-880e3aee9905", "d4ede701-8037-488b-9794-9b8632c1c3c0", "3066446c-5e9b-4321-bdf6-a47f367f61c5", "22656f17-0f99-438f-a934-b71d64a7fbd6", "b4517dc0-8202-4cff-be3e-c11a1f78037c", "fc87ba60-6c43-4420-bdb0-eacc00ffbca5", "ca5124ab-0c2f-4224-88b1-f579a01d2522"}
# for s in ss:
#     print(s in str(bp))
# print("Employees directly involved in production or service" in str(bp))

# pprint(bp)
# flattener = Flattener()
# mbn = MultiNetwork()
# guids_by_bn = flattener(bp, flag_generate_plus_one=True)
# # pprint(guids_by_bn)
# # exit()
# out = mbn.predict_all(guids_by_bn)
# pprint(out)

# print(findall('03f70344-c4f5-456a-bbfe-94dde489b31c', str(bp)))
# print(bp['plan'].keys())
# pprint(bp['plan']['channels'][0])

# pprint(bp['plan']['custSegs']['consumer'])
# exit()

# pprint(bp['plan']['costs']['fixedCosts'])
# pprint([a for a in bp['plan']['costs']['variableCosts'] if a['name'] == "aaa"])
# pprint(bp['plan']['costs']['fixedCosts'])
# pprint(bp['plan']['costs']['variableCosts'])
# exit()

# pprint(bp['plan']['swot'].keys())
# pprint(bp['plan']['swot']['strengths'])

# pprint(bp['plan']['keyPartners'].keys())
# pprint(bp['plan']['keyPartners']['distributors'][0])
# pprint(bp['plan']['keyPartners']['suppliers'][0])
# pprint(bp['plan']['keyPartners']['others'][0])

# pprint(bp['plan']['keyActivities'][0])
pprint(bp['plan']['keyResources'][-1])
# pprint(bp['plan']['custRelationship'])
# pprint(bp['plan']['revenue']['consumer'][0].keys())
# pprint(bp['plan']['revenue']['business'][0]["price"])
# pprint(bp['plan']['revenue'].keys())
