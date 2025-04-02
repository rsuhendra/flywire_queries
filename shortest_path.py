import graph_tool.all as gt
import numpy as np
import pandas as pd
from graphviz import Digraph
import re
import pickle
from collections import defaultdict, Counter
from scipy.sparse import coo_matrix, csr_matrix


def percentage_threshold(g, threshold = 50, mode = 'in'):
	csr_mat = gt.adjacency(g, weight=g.ep.weight)
 
	if mode == 'out':
		csr_mat = csr_mat.T.tocsr()
 
	# Initialize lists to store the new data, indices, and indptr
	new_data = []
	new_indices = []
	new_indptr = [0]
 
	for i in range(csr_mat.shape[0]):
		row = csr_mat.getrow(i)  # Get the i-th row
		nonzero_values = row.data  # Nonzero values in the row
		nonzero_indices = row.indices  # Indices of nonzero values

		if len(nonzero_values) > 0:
			perc = np.percentile(nonzero_values, 100 - threshold)  # Calculate the percentile

			# Compare each nonzero value to perc and replace with 1 or -1
			modified_values = np.where(nonzero_values > perc, 1, -1)

			# Append the modified values and indices to the lists
			new_data.extend(modified_values)
			new_indices.extend(nonzero_indices)
		
		new_indptr.append(new_indptr[-1] + len(nonzero_values))

	new_csr_mat = csr_matrix((new_data, new_indices, new_indptr), shape=csr_mat.shape)
	
	if mode == 'out':
		return new_csr_mat.T.tocsr()
	else:
		return new_csr_mat

def sp_subgraph(g, g_empty, sources, targets, gt_dicts, max_path_length = 4, mw_thresh = None, perc_thresh = None, remove = None):
	v_id, type_map, side_map, ntcmap = gt_dicts
	
	if mw_thresh != None:
		u = gt.GraphView(g, efilt = (g.ep.weight.a >=  mw_thresh))
		print('Done thresholding by weight!')

	
	if perc_thresh != None:
		new_adj = percentage_threshold(g, threshold = perc_thresh, mode = 'in')
		u = gt.GraphView(g, efilt = (new_adj.data > 0))
		print('Done thresholding by percentage!')
  
		# u = g_empty.copy()
		# print(g)
		# print(g.ep.weight.a.shape)

		# new_adj = percentage_threshold(g, threshold = perc_thresh, mode = 'out')
		# count = 0
		# print(f'Remaking graph with {new_adj.nnz} edges!')
	
		# for i, j in zip(new_adj.col, new_adj.row):
		# 	new_edge = u.add_edge(i, j)
		# 	u.ep.weight[new_edge] = g.ep.weight[g.edge(i, j)]
		# 	u.ep.nt[new_edge] = g.ep.nt[g.edge(i, j)]
		# 	count+=1

		# 	if count%1000 == 0:
		# 		print(count)

		# print('Done thresholding by percentage!')
	
	# Remove specified neurons from graph
	if remove is not None:
		for r in remove:
			g.remove_vertex(v_id[r])
 
 
	u2 = g_empty.copy()
 
	# Actual shortest path stuff
	for s in sources:
		for t in targets:
			for path in gt.all_shortest_paths(u, v_id[s], v_id[t]):
				if len(path) > max_path_length: # if path too long, skip
					continue
				for i in range(len(path)-1):
					if not u2.edge(path[i], path[i+1]):
						new_edge = u2.add_edge(path[i], path[i+1])
						u2.ep.weight[new_edge] = u.ep.weight[g.edge(path[i], path[i+1])]
						u2.ep.nt[new_edge] = u.ep.nt[g.edge(path[i], path[i+1])]
 
	# Remove vertices with no edges
	isolated_vertices = []
	for v in u2.vertices():
		if v.out_degree() == 0 and v.in_degree() == 0:
			isolated_vertices.append(v)
	u2.remove_vertex(isolated_vertices)
	
	return u2


def plot_graphviz(g, ntcmap, nameSource, nameTarget, mw, mpl, restrict_type=None, plotdir = 'figs'):
	dot = Digraph(strict=True)
 
	# Legend for Neurotransmitter colors
	for key, value in ntcmap.items():
		if key == None:
			dot.node('None', color=value, style='filled', shape='rarrow')
		else:
			dot.node(key, color=value, style='filled', shape='rarrow')
   
	for e in g.edges():
		type1 = g.vp.type[e.source()]
		type2 = g.vp.type[e.target()]

		# Restrict plotting to only those of specified types
		if restrict_type is not None:
			if not ((type1 in restrict_type) and (type2 in restrict_type)):
				continue
		
		n0 = str(g.vp.name[e.source()]) + '\n(' + type1 + ')'
		n1 = str(g.vp.name[e.target()]) + '\n(' + type2 + ')'
		dot.edge(n0, n1, label = str(g.ep.weight[e]), color = ntcmap[g.ep.nt[e]])

		# Color source and target nodes for vis
		if g.vp.type[e.source()] in nameSource:
			dot.node(n0,shape='box', color='orange', style='filled')
		elif g.vp.type[e.target()] in nameTarget:
			dot.node(n1,shape='box',color='yellow', style='filled')
        
	dot.format='png'
	if restrict_type is None:
		title = f'({nameSource})_({nameTarget})_mw={mw}_mpl={mpl}'
	else:
		title = f'({nameSource})_({nameTarget})_mw={mw}_mpl={mpl}_restricted'
	dot.render(title,cleanup=True,view=False,directory=plotdir)


def plot_graphviz_consolidated(g, ntcmap, type_count, nameSource, nameTarget, mw, mpl,ratio_thresh=None, abs_thresh = None, plotdir = 'figs'):
	
	consolidated_dict = defaultdict(list)
	consolidated_nt = defaultdict(list)
	for e in g.edges():
		source_type = g.vp.type[e.source()]
		target_type = g.vp.type[e.target()]
		consolidated_dict[(source_type, target_type)].append(g.ep.weight[e])
		consolidated_nt[(source_type, target_type)].append(g.ep.nt[e])
	dot = Digraph(strict=True)
 
	for key, val in consolidated_dict.items():
		n0 = key[0]+ f'\ntot={type_count[key[0]]}'
		n1 = key[1]+ f'\ntot={type_count[key[1]]}'
		
		# Limit based on ratio between types of all to all connections
		if ratio_thresh is not None:
			ratio = len(val)/(type_count[key[0]]*type_count[key[1]])
			if ratio<ratio_thresh:
				continue
		
		if abs_thresh is not None:
			if len(val) <= abs_thresh:
				continue

		most_common_nt_color = ntcmap[Counter(consolidated_nt[key]).most_common(1)[0][0]]
		dot.edge(n0, n1, label = f'n={len(val)},avg={np.average(val)}', color = most_common_nt_color)
		
		# Color source and target nodes for vis
		if key[0] in nameSource:
			dot.node(n0,shape='box', color='orange', style='filled')
		elif key[1] in nameTarget:
			dot.node(n1,shape='box',color='yellow', style='filled')
 
	# Legend for Neurotransmitter colors
	for key, value in ntcmap.items():
		if key == None:
			dot.node('None', color=value, style='filled', shape='rarrow')
		else:
			dot.node(key, color=value, style='filled', shape='rarrow')
   
	dot.format='png'
	# if thresh is None:
	title = f'consolidated_({nameSource})_({nameTarget})_mw={mw}_mpl={mpl}'
	# else:
	# 	title = f'consolidated_({nameSource})_({nameTarget})_mw={mw}_mpl={mpl}_thresh={thresh}'
	dot.render(title,cleanup=True,view=False,directory=plotdir)

