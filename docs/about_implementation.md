## Bayes Network expression limitations
BNs can't naturally express a lot of structures. For example 
multiple consumer/business/ngo segments in ono business plan.

This problem is remedied by dividing business plan in many
smaller BNs - one main BN and for each such situation as described 
previously has it's own BN.

The smaller BNs have evidence nodes where put some global info.

## Data flattening and processing
Incoming BP is flattened in list of elemnds ``list<bn_name, list<evidence_guids>>``, thats
becouse guids are not global (becouse multiple consumer segments possible).

Then each of the master list tuples are processed with pysmile BNs.

After that the form ``list<bn_name, list<predicted_guids>>`` ir again transformed
back to BP in the same format as input. Check test script for this transformation
in script ``tests/checking_back_and_forward_transformation.py``.

## On code/model/data changes
Subnetworks that needs to be treated the same way as consumer/business/ngo segments
needs to be listed in ``docs/bp_flatten_names_to_bns.json`` together with their
guid parts.

In last steps of the processing elements of``list<bn_name, list<predicted_guids>>`` are
merged together. If merger is merged BPs in on level - it won't merger lower
levels in the json hierarchy. Merger assumes all BPs has the same form as full_bp.json.
Merger uses md5 hashes of subjsons to recognize some situations.

