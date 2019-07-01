#!/usr/bin/env python
# -*- coding: utf-8 -*-*
# import matplotlib.pyplot as plt
import networkx as nx
import pickle
import codecs
import os
import time
start = time.time()

#dataset_dir = "/Users/sina/OneDrive - National University of Ireland, Galway/Documentation/TIAD/Source code"
dataset_dir = "TranslationSetsApertiumRDF"
file_list = list()
for file_name in os.listdir(dataset_dir):
	if file_name.endswith(".tsv"):
		file_list.append(file_name)

def get_path_frequency(paths):
	paths_freq = {i: 0 for i in range(20)} 
	for path in paths:
		paths_freq[len(path)] += 1

	for key, value in paths_freq.items():
		print key, value
# ============================================================
#	
# ============================================================
def get_chain_languages(lang_list):
	lang_chain = list()
	for index in range(1, len(lang_list)):
		if index < len(lang_list):
			lang_chain.append(lang_list[index-1] + "-" + lang_list[index])
	return lang_chain

def read_dict(word, lang_chain):
	"""returns a list of the edge word translations """
	lang_dict = pickle.load( open( dataset_dir + "/" + lang_chain + ".pickle", "rb" ) )
	if word in lang_dict.keys():
		return lang_dict[word]
	else:
		return[""]

def word_to_node(language, word):
	return u' '.join((language, word)).encode('utf-8').strip()
# ============================================================
#	Draw graph
# ============================================================
def draw_graph(G_nodes):
	G = nx.DiGraph()
	# Draw the translation graph
	G.add_edges_from(G_nodes)
	# pos=nx.graphviz_layout(G, prog='dot')
	pos = nx.kamada_kawai_layout(G)
	nx.draw(G, pos, node_size=400, node_color="cyan", with_labels = True)
	plt.show()
# ============================================================
#	Create dictionary data structure from the TSV files
# ============================================================
def create_dictionary(file_list):
	""" Create dictionaries """
	for file_name in file_list:
		print file_name
		in_file = codecs.open(dataset_dir + "/" + file_name, "r", "utf-8").read().split("\n")
		in_file_dict, in_file_reverse_dict = dict(), dict()
		for entry in in_file:
			w_source, w_target, pos = entry.split(" \t ")[0][1:-1], entry.split(" \t ")[1][1:-1], entry.split(" \t ")[2][1:-1]
			# Fix the "http://..." problem.
			# if "http://" in words[1]:
			# 	print words
			key = w_source + " " + pos
			target = w_target + " " + pos
			if key not in in_file_dict.keys():
				in_file_dict[key] = [target]
			else:
				if target not in in_file_dict[key]:
					in_file_dict[key].append(target)

			key = w_target + " " + pos
			target = w_source + " " + pos
			if key not in in_file_reverse_dict.keys():
				in_file_reverse_dict[key] = [target]
			else:
				if target not in in_file_reverse_dict[key]:
					in_file_reverse_dict[key].append(target)

		# for key, value in in_file_dict.items()[0:30]:
		# 	print key, value
		# for key, value in in_file_reverse_dict.items()[0:30]:
		# 	print key, value
		pickle.dump(in_file_dict, open( str(dataset_dir + "/" + file_name[:-3]+"pickle"), "wb" ) )
		pickle.dump(in_file_reverse_dict, open( str(dataset_dir + "/" + ((file_name[:-3].split("-")[1])[:-1] + "-" + file_name[:-3].split("-")[0]) + ".pickle"), "wb" ) )
# ============================================================
#	Create translation pairs
# ============================================================
def create_translation_pairs(G_nodes, source, target):
	translations = dict()
	for index in reversed(range(len(G_nodes))):
		if G_nodes[index][1].split()[0] == target:
			if len(G_nodes[index][1]) > 2:
				trans_word = G_nodes[index][1].lower()
				if trans_word not in translations:
					translations[trans_word] = 1
				else:
					translations[trans_word] += 1
		else:
			break
	return translations
# ============================================================
#	Extract translations and return as a graph.
# ============================================================
def extract_translations_graph(word_source, paths):
	graph_collection = list()	# graph structure
	path_dictionary = dict() # translation paths
	for path in paths[1:5]:
		G_nodes = list()
		path_translations = dict()
		lang_chain_words = [[word_source]]
		lang_chain = get_chain_languages(path)

		for edge in lang_chain:
			language_from, language_to = edge.split("-")[0], edge.split("-")[1]
			word_trans = list()
			for word in lang_chain_words:
				for sub_word in word:
					sub_word_translation = read_dict(sub_word, edge)
					word_trans.append(sub_word_translation)

					for sbt in sub_word_translation:
						G_nodes.append( (word_to_node(language_from, sub_word), word_to_node(language_to, sbt)) )

			lang_chain_words = word_trans#read_dict(word, edge)
			path_translations[edge] = word_trans

		path_dictionary[str(path)] = path_translations
		graph_collection.append(G_nodes)

		# for n in G_nodes:
		# 	print n
		# Print the path_translations
		# for key in lang_chain:
		# 	print key, path_translations[key], len(path_translations[key])

	return graph_collection
# ============================================================
#	Main
# ============================================================
G = nx.Graph()
nodes = ["IT", "OC", "PT", "GL", "RO", "AST", "AN", "EU", "EN", "EO", "FR", "CA", "ES"]
edges = [("IT", "CA"),
		("CA", "FR"), ("CA", "EO"), ("CA", "EN"), ("CA", "ES"), ("CA", "PT"), ("CA", "OC"),
		("ES", "EU"), ("ES", "AN"), ("ES", "AST"), ("ES", "RO"), ("ES", "GL"), ("ES", "PT"), ("ES", "OC"), ("ES", "FR"), ("ES", "EO"), ("ES", "EN"),
		("PT", "GL"),
		("FR", "EO"),
		("EO", "EN"),
		("EN", "EU"), ("EN", "GL")
		]
G.add_nodes_from(nodes)
G.add_edges_from(edges)

# create_dictionary(file_list)
source="EN"
target="PT"
start_id = 0
stop_id = 1

paths = nx.all_simple_paths(G, source, target, cutoff=100)
# paths_new = list()
# # remove EO (Esperanto) due to file problems. 
# for path in list(paths):
# 	if "EO" not in path:
# 		paths_new.append(path)
paths = list(paths)
print source, target, len(paths)

if True:
	# ======
	# Print the translation of a specific word and a specific path
	source_word = "spring noun"
	for path in paths[0:1]:
		print path
	# paths = paths[0:1]
	# ======

	EN_words = pickle.load( open(dataset_dir+"/EN-ES.pickle", "rb")).keys()
	FR_words = pickle.load( open(dataset_dir+"/FR-ES.pickle", "rb")).keys()
	PT_words = pickle.load( open(dataset_dir+"/PT-ES.pickle", "rb")).keys()

	print len(EN_words), len(FR_words), len(PT_words)	
	#	23128 19763 11380

	WORDS = list()
	if source == "EN":
		WORDS = EN_words
	elif source == "PT":
		WORDS = PT_words
	elif source == "FR":
		WORDS = FR_words

	WORDS = [source_word]

	source_target_dictionary = dict()

	counter = 0
	for word in WORDS[start_id:stop_id]:
		# Ignore multi-word entries
		if len(word.split()) <3:
			word = word.lower()
			graph_collection = extract_translations_graph(word, paths )

			for g in graph_collection:
				print g

			for G_nodes in graph_collection:
				translations = create_translation_pairs(G_nodes, source, target)

			translations_collection = dict()
			for key in translations:
				if key in translations_collection.keys():
					translations_collection[key] += translations[key]
				else:
					translations_collection[key] = translations[key]
			print word, translations_collection
			source_target_dictionary[word] = translations_collection

# 	counter += 1
# 	if counter % 10 == 0:
# 		print str(counter*100 / (stop_id - start_id)) + "%"

# pickle.dump( source_target_dictionary, open( "Translations/" + source + "-" + target + "-" + str(start_id) + ".p", "wb" ) )
# print "Output pickled."



# print source_target_dictionary

# print "EN to PT", list(paths)
# paths = nx.all_simple_paths(G, source="FR", target="PT", cutoff=100)
# print "FR to PT", len(list(paths))
# paths = nx.all_simple_paths(G, source="FR", target="EN", cutoff=100)
# print "FR to EN", list(paths)

# Plot graph
# pos = nx.kamada_kawai_layout(G)
# nx.draw(G, pos, node_size=400, node_color="cyan", with_labels = True)
# plt.show()

end = time.time()
print end-start