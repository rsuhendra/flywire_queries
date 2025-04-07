from search_functions import *
from shortest_path import *
from collections import Counter


# fname = 'connections_princeton_no_threshold'
fname = 'connections'	# automatically thresholded with weight 5
# fname = 'connections_no_threshold'

# data_dir = '../../flywire_data'
data_dir = 'flywire_data'

g = gt.load_graph(f'{data_dir}/{fname}.gt')
g_empty = gt.load_graph(f'{data_dir}/{fname}_empty.gt')
gt_dicts = pickle.load(open( f"{data_dir}/{fname}_dicts.pkl", "rb" ))

v_id, type_map, side_map, ntcmap = gt_dicts

# Zexin: The nameSource search term here is based on Regex, ask me if u dont know it. 
nameSource, side = 'hDeltaC', None
sources, source_types, source_term = search_neurons(nameSource, gt_dicts, side=side)

# # Zexin: Code here for multiple types:
# nameSources = ['hDeltaC', 'EPG']
# sources, source_types, source_term = [], [], []
# for nameSource in nameSources:
# 	ss, sty, stm = search_neurons(nameSource, gt_dicts, side=side)
# 	sources.append(ss) 
# 	source_types.append(sty)
# 	source_term.append(stm)


nameTarget, side = 'PFL3', None
targets, target_types, target_term = search_neurons(nameTarget, gt_dicts, side=side, exact = None)

# print(f'Removing!')
# nameRemove, side = 'FC2', None
# remove, _, _ = search_neurons(nameRemove, gt_dicts, side=side, exact = None)

# Zexin: mw = minimum weight threshold, mpl = max path length

mw = 5
mpl = 4
sp_g = sp_subgraph(g, g_empty, sources, targets, gt_dicts, max_path_length = mpl, mw_thresh = mw, perc_thresh = None, remove = None)
plotdir = 'figs'

# Possible restrictions

restrict = None
# restrict = ['TRN_VP2', 'M_l2PNm14', 'VP2+_adPN', 'FB1G', 'FC2A', 'FB5AB', 'FB5A', 'FB4N'] 
# 'vDeltaF,vDeltaG,vDeltaH,vDeltaI', 'hDeltaJ'


plot_graphviz(sp_g, ntcmap, nameSource, nameTarget, mw, mpl, restrict_type=restrict, plotdir = plotdir)

neuron_class = pd.read_csv('../../flywire_data/classification_fillna.csv')
type_count = Counter(neuron_class.consensus_type)
plot_graphviz_consolidated(sp_g, ntcmap, type_count, nameSource, nameTarget, mw, mpl, abs_thresh = None, plotdir = plotdir)