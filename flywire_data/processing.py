import graph_tool.all as gt
import numpy as np
import pandas as pd
from graphviz import Digraph
import re
import pickle

fname = 'connections_princeton_no_threshold'
# fname = 'connections'
# fname = 'connections_no_threshold'

# preProcess by adding up parallel edges
# df = pd.read_csv(f'{fname}.csv')
# df['nt_type'] = df['nt_type'].fillna(value='None')
# df_combined = df.groupby(['pre_pt_root_id', 'post_pt_root_id'], as_index=False).agg({
#     'syn_count': 'sum',  # Sum numerical column
#     'nt_type': lambda x: x.mode().iloc[0]  # Most common value
# })
# df_combined = df_combined.sort_values(by=['pre_pt_root_id', 'post_pt_root_id'])
# df_combined.to_csv(f'{fname}_combined.csv', index=False)  

# del df, df_combined

# Create graph
g = gt.load_graph_from_csv(f'{fname}_combined.csv', directed=True, skip_first=True, eprop_types=['int', 'string'], eprop_names=['weight', 'nt'], hash_type='long')

# dictionary mapping name to vertex (faster than using find_vertex)
v_id = dict(zip(list(g.vp.name.a), np.arange(g.num_vertices())))
# v_id = lambda x : gt.find_vertex(g, g.vp.name, x)[0]

# Helper function for getting edge weights
# edge_weight = lambda x, y, g : g.ep.weight[g.edge(x, y)]


# Create type map
df = pd.read_csv('classification.csv')
df['consensus_type'] = df['hemibrain_type'].fillna(df['cell_type'], inplace=False)
df['consensus_type'].fillna('NoType', inplace=True)
df['side'].fillna('None', inplace=True)


# Restrict to those that have connections
df = df[df['root_id'].isin(list(g.vp.name.a))]

type_map = dict(zip(df['root_id'], df['consensus_type']))
side_map = dict(zip(df['root_id'], df['side']))

# Create Vertex Map for neuron type and side
type_name = g.new_vertex_property("string")
side = g.new_vertex_property("string")
for v in g.iter_vertices():    
	type_name[v] = type_map[g.vp.name[v]]
	side[v] = side_map[g.vp.name[v]]
g.vp.type = type_name
g.vp.side = side

# Neurotransmitter colormap
nt_types = ['ACH', 'GABA', 'GLUT', 'DA', 'OCT', 'SER', None, 'None']
nt_colors = ['red', 'blue', 'green', 'purple', 'pink', 'cyan', 'grey', 'grey']
ntcmap = dict(zip(nt_types, nt_colors))

g.save(f'{fname}.gt', fmt = 'gt')

# Save empty version
g.clear_edges()
g.save(f'{fname}_empty.gt', fmt = 'gt')

pickle.dump((v_id, type_map, side_map, ntcmap), open(f'{fname}_dicts.pkl', "wb"))



# HOW TO LOAD
# g = gt.load_graph('flywire/flywire.gt')
# v_id, type_map, side_map, ntcmap = pickle.load(open( "flywire/flywire_dicts.pkl", "rb" ))
