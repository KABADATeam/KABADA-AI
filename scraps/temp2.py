import pandas as pd
from config import path_temp_data_file
from collections import Counter
from pprint import pprint

# tab = pd.read_csv(path_temp_data_file, sep=" ")
# print(tab.shape)
# print(tab.columns)
# for c in tab.columns:
#     counter = Counter(tab[c])
#     print(c, counter, len(counter))

guids_by_bn = [('key_partners_others', ['plan::keyPartners::others::priority::True', 'plan::keyPartners::others::id::08007db6-d70c-435e-bec8-0063ef6c9eec'], '08007db6-d70c-435e-bec8-0063ef6c9eec'), ('key_partners_others', ['plan::keyPartners::others::priority::True', 'plan::keyPartners::others::id::99e57733-0605-4632-b52e-cee9db2b2172'], '99e57733-0605-4632-b52e-cee9db2b2172'), ('key_partners_suppliers', ['plan::keyPartners::suppliers::priority::False', 'plan::keyPartners::suppliers::id::966b338a-d20e-4774-9b0f-eb4dbc3208a3'], '966b338a-d20e-4774-9b0f-eb4dbc3208a3'), ('key_partners_suppliers', ['plan::keyPartners::suppliers::priority::False', 'plan::keyPartners::suppliers::id::2d618fcb-5dd1-4841-bb2f-b3b4ff06a3ba'], '2d618fcb-5dd1-4841-bb2f-b3b4ff06a3ba'), ('key_partners_distributors', ['plan::keyPartners::distributors::priority::True', 'plan::keyPartners::distributors::id::9fbbf494-0d2b-458e-a174-27bfd1b0a96a'], '9fbbf494-0d2b-458e-a174-27bfd1b0a96a'), ('key_partners_distributors', ['plan::keyPartners::distributors::priority::True', 'plan::keyPartners::distributors::id::62b76e8d-6f2f-4914-8948-b02e77181e5b'], '62b76e8d-6f2f-4914-8948-b02e77181e5b'), ('revenue_streams_business', ['plan::revenue::business::segments::12e06d95-0f37-4732-9363-a8e5f7376b88', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::fed203b7-dbb4-4410-9698-ed8f0c1798df', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::553b3235-8e2e-449e-9096-0cbd31d176de', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::beb99b8c-5bc4-4ef7-ae27-547d17aaab15', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::dec35e95-c079-48e4-b49f-ff03c0cea3cc', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::9b1adb6c-a9fe-4ded-98ac-69c6273cafcc', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::2ad5c353-e3f5-45b8-9fd9-4de29994ad5b', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::a7e10d01-44ed-4d05-8094-14e2a748509f', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::2a70051b-20f5-422a-8508-1a8d5f954030', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::7b205233-e4d2-4276-a654-8b13d4b61934', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::ce5768ca-16f7-4b06-af72-06eadb85ce09', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::segments::56ea8f2c-5bc9-4648-8d96-6931f90e4204', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_business', ['plan::revenue::business::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::business::segments::1a58be72-3773-4210-afbb-9ce6cd646a87', 'plan::revenue::business::id::e53c493f-98e6-4225-b64d-ff701b5960c0'], 'e53c493f-98e6-4225-b64d-ff701b5960c0'), ('revenue_streams_consumers', ['plan::revenue::consumer::segments::69dcb8eb-5ef4-4150-aa66-610437948022', 'plan::revenue::consumer::id::ed0de75d-995e-4a34-a224-244363fdd1be'], 'ed0de75d-995e-4a34-a224-244363fdd1be'), ('revenue_streams_ngo', ['plan::revenue::publicNgo::pricingType::363f16df-3f11-4643-9c93-cd64242c0bf5', 'plan::revenue::publicNgo::segments::678fe09b-f721-440a-898f-97ce8e35b9ee', 'plan::revenue::publicNgo::id::66160a8b-3f0a-4678-8567-70062b525ed0'], '66160a8b-3f0a-4678-8567-70062b525ed0'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::12e06d95-0f37-4732-9363-a8e5f7376b88'], '12e06d95-0f37-4732-9363-a8e5f7376b88'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::fed203b7-dbb4-4410-9698-ed8f0c1798df'], 'fed203b7-dbb4-4410-9698-ed8f0c1798df'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::553b3235-8e2e-449e-9096-0cbd31d176de'], '553b3235-8e2e-449e-9096-0cbd31d176de'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::beb99b8c-5bc4-4ef7-ae27-547d17aaab15'], 'beb99b8c-5bc4-4ef7-ae27-547d17aaab15'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::dec35e95-c079-48e4-b49f-ff03c0cea3cc'], 'dec35e95-c079-48e4-b49f-ff03c0cea3cc'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::9b1adb6c-a9fe-4ded-98ac-69c6273cafcc'], '9b1adb6c-a9fe-4ded-98ac-69c6273cafcc'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::2ad5c353-e3f5-45b8-9fd9-4de29994ad5b'], '2ad5c353-e3f5-45b8-9fd9-4de29994ad5b'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::a7e10d01-44ed-4d05-8094-14e2a748509f'], 'a7e10d01-44ed-4d05-8094-14e2a748509f'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::2a70051b-20f5-422a-8508-1a8d5f954030'], '2a70051b-20f5-422a-8508-1a8d5f954030'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::7b205233-e4d2-4276-a654-8b13d4b61934'], '7b205233-e4d2-4276-a654-8b13d4b61934'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::ce5768ca-16f7-4b06-af72-06eadb85ce09'], 'ce5768ca-16f7-4b06-af72-06eadb85ce09'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::56ea8f2c-5bc9-4648-8d96-6931f90e4204'], '56ea8f2c-5bc9-4648-8d96-6931f90e4204'), ('business_segments', ['plan::custSegs::business::company_size::37634235-3b04-4aad-a647-6d79a2c88655', 'plan::custSegs::business::company_size::bbc364e1-2394-48c7-8aaf-774ba76942b6', 'plan::custSegs::business::company_size::a2254a01-9908-42e0-af0d-8a0b04875197', 'plan::custSegs::business::id::1a58be72-3773-4210-afbb-9ce6cd646a87'], '1a58be72-3773-4210-afbb-9ce6cd646a87'), ('consumer_segments', ['plan::custSegs::consumer::education::bbab5ef4-bbd3-44aa-a879-1a792a5feada', 'plan::custSegs::consumer::education::4718bb8b-3018-4408-9ff1-68ab9c4f2b87', 'plan::custSegs::consumer::education::bc6e314f-5d86-40dc-a791-d63be99c22bd', 'plan::custSegs::consumer::income::bdb6d057-80b7-411a-a6b6-12aae71581c3', 'plan::custSegs::consumer::income::d2a35000-6520-47fb-921a-1968a38f6eb8', 'plan::custSegs::consumer::income::b30ffa71-9656-4f10-be64-cd92bad378c0', 'plan::custSegs::consumer::id::69dcb8eb-5ef4-4150-aa66-610437948022'], '69dcb8eb-5ef4-4150-aa66-610437948022'), ('channels', ['plan::channels::subtypeType::4152d046-a8a2-4adc-a6b3-b2de8c3cafbf', 'plan::channels::distributionChannels::ee238326-5d11-4531-92b0-6565f42ae874', 'plan::channels::distributionChannels::b2706a04-d62f-4103-ae40-6b5868029c73', 'plan::channels::products::f330dee8-1eed-474b-89ec-6f9e8dd0ad0e', 'plan::channels::products::c095b0e6-353d-4430-bb0c-48e4bd2874de', 'plan::channels::id::f3d5a045-d06e-4277-b09c-93548a5884f3'], 'f3d5a045-d06e-4277-b09c-93548a5884f3'), ('channels', ['plan::channels::subtypeType::4152d046-a8a2-4adc-a6b3-b2de8c3cafbf', 'plan::channels::products::d5916c5e-41a1-4858-ab30-51609e49e7df', 'plan::channels::products::c095b0e6-353d-4430-bb0c-48e4bd2874de', 'plan::channels::id::f3d5a045-d06e-4277-b09c-93548a5884f3'], 'f3d5a045-d06e-4277-b09c-93548a5884f3'), ('value_propositions', ['plan::valueProposition::priceLevel::3325759e-8add-4b30-a00c-10ce7fbbd330', 'plan::valueProposition::addIncomeSource::fe928bb7-8ef0-4f01-b40b-f7da62c1c084', 'plan::valueProposition::productFeatures::2984418a-638e-4da9-be1d-12ba94d8ffaf', 'plan::valueProposition::productFeatures::bdf69fe7-c3e3-44e1-a984-41041ea08e96', 'plan::valueProposition::productFeatures::0ff6b626-a1ff-4184-b1bb-5bf2992091bd', 'plan::valueProposition::productFeatures::4cb290b2-7fbc-4846-be7b-79f9e3efbb46', 'plan::valueProposition::productFeatures::07d5452f-6ea6-4ae6-9395-89fd1d0eeab0', 'plan::valueProposition::productFeatures::7baa945c-4bcb-46b9-8e95-c72fe5b49778', 'plan::valueProposition::id::c095b0e6-353d-4430-bb0c-48e4bd2874de'], 'c095b0e6-353d-4430-bb0c-48e4bd2874de'), ('value_propositions', ['plan::valueProposition::priceLevel::3325759e-8add-4b30-a00c-10ce7fbbd330', 'plan::valueProposition::productFeatures::2984418a-638e-4da9-be1d-12ba94d8ffaf', 'plan::valueProposition::productFeatures::bdf69fe7-c3e3-44e1-a984-41041ea08e96', 'plan::valueProposition::productFeatures::0ff6b626-a1ff-4184-b1bb-5bf2992091bd', 'plan::valueProposition::productFeatures::4cb290b2-7fbc-4846-be7b-79f9e3efbb46', 'plan::valueProposition::productFeatures::07d5452f-6ea6-4ae6-9395-89fd1d0eeab0', 'plan::valueProposition::productFeatures::7baa945c-4bcb-46b9-8e95-c72fe5b49778', 'plan::valueProposition::id::f330dee8-1eed-474b-89ec-6f9e8dd0ad0e'], 'f330dee8-1eed-474b-89ec-6f9e8dd0ad0e'), ('value_propositions', ['plan::valueProposition::priceLevel::3325759e-8add-4b30-a00c-10ce7fbbd330', 'plan::valueProposition::addIncomeSource::fe928bb7-8ef0-4f01-b40b-f7da62c1c084', 'plan::valueProposition::productFeatures::2984418a-638e-4da9-be1d-12ba94d8ffaf', 'plan::valueProposition::productFeatures::bdf69fe7-c3e3-44e1-a984-41041ea08e96', 'plan::valueProposition::productFeatures::0ff6b626-a1ff-4184-b1bb-5bf2992091bd', 'plan::valueProposition::productFeatures::07d5452f-6ea6-4ae6-9395-89fd1d0eeab0', 'plan::valueProposition::productFeatures::7baa945c-4bcb-46b9-8e95-c72fe5b49778', 'plan::valueProposition::id::d5916c5e-41a1-4858-ab30-51609e49e7df'], 'd5916c5e-41a1-4858-ab30-51609e49e7df'), ('value_propositions', ['plan::valueProposition::priceLevel::3325759e-8add-4b30-a00c-10ce7fbbd330', 'plan::valueProposition::productFeatures::2984418a-638e-4da9-be1d-12ba94d8ffaf', 'plan::valueProposition::productFeatures::bdf69fe7-c3e3-44e1-a984-41041ea08e96', 'plan::valueProposition::productFeatures::0ff6b626-a1ff-4184-b1bb-5bf2992091bd', 'plan::valueProposition::productFeatures::07d5452f-6ea6-4ae6-9395-89fd1d0eeab0', 'plan::valueProposition::productFeatures::7baa945c-4bcb-46b9-8e95-c72fe5b49778', 'plan::valueProposition::id::7f53265d-7222-4b1c-9d26-4e56008bd662'], '7f53265d-7222-4b1c-9d26-4e56008bd662'), ('plan', ['plan::swot::strengths::e0c84bf6-dbc3-450e-95ac-fe42299e05df', 'plan::swot::threats::ab5ffc0e-da10-4ed8-a7fb-369785911381'], None)]

pprint(guids_by_bn)