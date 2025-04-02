import graph_tool.all as gt
import numpy as np
import pandas as pd
from graphviz import Digraph
import re
import pickle
from collections import defaultdict, Counter

def direct_edge(g, targets, gt_dicts, type_count, mw = 5, mode = 'in'):
	v_id, type_map, side_map, ntcmap = gt_dicts


	u = gt.GraphView(g, efilt = (g.ep.weight.a >=  mw))
	
	columns = ['Type', 'Weight']
	df = pd.DataFrame(columns=columns)
	i = 0
	for t in targets:
		if mode == 'in':
			edges = u.get_in_edges(v_id[t], [g.ep.weight])
			p = 0
		if mode == 'out':
			edges = u.get_out_edges(v_id[t], [g.ep.weight])
			p = 1
   
		for e in edges:
			df.loc[i] = [u.vp.type[e[p]], e[2]]
			i+=1
	
	result = df.groupby('Type').agg(
		Count_of_Category=('Type', 'size'),   # Count occurrences of each category
		Average_Count=('Weight', 'mean')           # Calculate average of 'Count' column for each category
	).reset_index()
 
	result['Type_Count'] = result['Type'].map(type_count)
	result['Percent_of_total'] = 100*result['Count_of_Category']/(result['Type_Count']*len(targets))
 
	return result