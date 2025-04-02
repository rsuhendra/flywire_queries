from search_functions import *
from shortest_path import *
from direct_connections import *
from collections import Counter


fname = 'connections'

g = gt.load_graph(f'../../flywire_data/{fname}.gt')
g_empty = gt.load_graph(f'../../flywire_data/{fname}_empty.gt')
gt_dicts = pickle.load(open( f"../../flywire_data/{fname}_dicts.pkl", "rb" ))

v_id, type_map, side_map, ntcmap = gt_dicts

nameTarget, side = 'FB5I', None
targets, target_types, target_term = search_neurons(nameTarget, gt_dicts, side=side, exact = True)

neuron_class = pd.read_csv('../../flywire_data/classification_fillna.csv')
type_count = Counter(neuron_class.consensus_type)


restrictions = [None, 2, 5]
modes = ['in', 'out']
for restrict in restrictions:
	for mode in modes:
		result = direct_edge(g, targets, gt_dicts, type_count, mw = 5, mode = mode)
		if restrict is None:
			result.to_csv('data/'+nameTarget + '_' + mode + '.csv', index=False)
		else:
			initial_count = len(result)
			result = result[result['Percent_of_total'] >= restrict]
			print(f"Rows removed: {initial_count-len(result)} out of {initial_count}")
			result.to_csv('data/'+nameTarget + '_' + mode + f'_restrict={restrict}'+'.csv', index=False)