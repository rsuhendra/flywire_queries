import graph_tool.all as gt
import numpy as np
import pandas as pd
from graphviz import Digraph
import re
import pickle

def search_neurons(term, gt_dicts, side = None):
	# Use a dictionary comprehension to filter the dictionary based on the regex condition
 
	v_id, type_map, side_map, ntcmap = gt_dicts
	
	if term[0] == '*':
		keys_result, values_result = zip(*[(key, value) for key, value in type_map.items() if term[1:]==value])
	else:
		keys_result, values_result = zip(*[(key, value) for key, value in type_map.items() if term in value])
 
	# pattern = re.compile(term)
	# if exact is None:
	# 	keys_result, values_result = zip(*[(key, value) for key, value in type_map.items() if pattern.search(value)])
	# else:
	# 	keys_result, values_result = zip(*[(key, value) for key, value in type_map.items() if pattern.fullmatch(value)])
     
	if side is None:
		print(f'For term {term} there are {len(keys_result)} neurons.')
		print(f'Types: {set(values_result)}')

		return list(keys_result), list(values_result), term

	else:
		keys_result2, values_result2 = [], []
		for j, key in enumerate(keys_result):
			if side_map[key] == side:
				keys_result2.append(keys_result[j])
				values_result2.append(values_result[j])
		
		print(f'For term {term} there are {len(keys_result2)} neurons.')
		print(f'Types: {set(values_result2)}')

		return keys_result2, values_result2, term+f'_{side}'