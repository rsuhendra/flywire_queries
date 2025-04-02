
def shortest_paths_fig(g, sources, targets, source_term, target_term, gt_dicts, max_path_length = 4, mw = 5):
    
	v_id, type_map, side_map, ntcmap = gt_dicts
    
	dot = Digraph(strict=True)

	# Legend for Neurotransmitter colors
	for key, value in ntcmap.items():
		if key == None:
			dot.node('None', color=value, style='filled', shape='rarrow')
		else:
			dot.node(key, color=value, style='filled', shape='rarrow')
	
	# u = gt.GraphView(g, vfilt = (g.get_out_degrees(np.arange(g.num_vertices()))< 200))
	u = gt.GraphView(g, efilt = (g.ep.weight.a >=  mw))

	# Actual shortest path stuff
	for s in sources:
		for t in targets:
			for path in gt.all_shortest_paths(u, v_id[s], v_id[t]):
				if len(path) > max_path_length: # if path too long, skip
					continue
				for i in range(len(path)-1):
					n0 = str(u.vp.name[path[i]]) + '\n(' + u.vp.type[path[i]] + ')'
					n1 = str(u.vp.name[path[i+1]]) + '\n(' + u.vp.type[path[i+1]] + ')'

					# Different box type and color for sources and targets
					if i == 0:
						dot.node(n0,shape='box', color='orange', style='filled')
					elif i == len(path)-2:
						dot.node(n1,shape='box',color='yellow', style='filled')

					dot.edge(n0, n1, label = str(u.ep.weight[u.edge(path[i], path[i+1])]), color = ntcmap[u.ep.nt[u.edge(path[i],path[i+1])]])
		
	dot.attr(label=f'\n Paths from {source_term} to {target_term}. \nMininimum weight is {mw}. Max path length is {max_path_length}',fontsize="25")

	dot.format='png'
	dot.render(f'({source_term})_({target_term})_mw{mw}_mpl{max_path_length}',cleanup=True,view=False,directory='temp')
 