#!/usr/bin/env python
# -*- coding: utf-8 -*-*
from __future__ import division
import pickle
import glob
import codecs

languages = {"EN": ["FR", "PT"], "FR": ["EN", "PT"], "PT": ["EN", "FR"]}
num_paths = ["4", "5", "6", "7"] # ["3",  already exists in 4

def merge_dicts(dict1, dict2, alpha=1, lngth=1):
	# dict1 should be the reference, dict2 the new one to be merge with dict1. 
	for key in dict2:
		if key not in dict1:
			dict1.update({key: {k: float(dict2[key][k])* (alpha ** lngth) for k in dict2[key]}})
		else:
			for value_key in dict2[key]:
				if value_key in dict1[key]:
					dict1[key][value_key] = dict1[key][value_key] + dict2[key][value_key] * (alpha ** lngth)
				else:
					dict1[key].update({value_key: float(dict2[key][value_key])* (alpha ** lngth) })
	return dict1

def collect_subdicts():
	# merge dictionaries within directories
	for path_num in num_paths:
		for lang in languages:
			datapath = "Translations/" + str(path_num) + "/" + str(lang) + "/Translations"
			for target_lang in languages[lang]:
				lang_code = lang + "-" + target_lang
				print path_num, lang_code
				lang_dic = dict()
				for file in glob.glob(datapath + "/*.p"):
					if lang_code in file:
						file_dict = pickle.load( open(file, "rb"))
						lang_dic = merge_dicts(lang_dic, file_dict)
				# write merged dictionaries
				pickle.dump(lang_dic, open(datapath + "/" + lang_code + ".p", "wb"))

#collect_subdicts()
def make_dictionaries():
	# count confidence based on alpha ** L(p) * frequency
	final_dict = dict()
	for lang in languages:
		for target_lang in languages[lang]:
			lang_dic = dict()
			for path_num in num_paths:
				datapath = "Translations/" + str(path_num) + "/" + str(lang) + "/Translations"
				lang_code = lang + "-" + target_lang
				for file in glob.glob(datapath + "/*.p"):
					if lang_code + ".p" == file.split("/")[-1]:
						print path_num, lang_code
						file_dict = pickle.load( open(file, "rb"))
						lang_dic = merge_dicts(lang_dic, file_dict, alpha=0.5, lngth=int(path_num))

			final_dict[lang_code] = lang_dic

	pickle.dump(final_dict, open("Translations/Final_translations.p", "wb"))

# make_dictionaries()

final_dict = pickle.load(open("Translations/Final_translations.p", "rb"))
for lang in final_dict.keys():
	print lang
	final_tsv = ""
	for key, value in final_dict[lang].items():#[0:15]
		summ = 0
		if len(value) != 0:
			# normalize value
			normalized_value = list()
			for v in value:
				summ += float(final_dict[lang][key][v])
			if lang == "EN-FR" or lang == "EN-PT":
				for v in value:
					final_tsv += " ".join( key.split()[:-1] ) + "\t" + " ".join( (v.decode("utf-8")).split()[1:-1] ) + "\t" + key.split()[-1] + "\t" + str(final_dict[lang][key][v]/summ) + "\n"
			else:
				for v in value:
					final_tsv += " ".join( key.split()[:-1] ) + "\t" + v.decode("utf-8") + "\t" + key.split()[-1] + "\t" + str(final_dict[lang][key][v]/summ) + "\n"

	file = codecs.open("Translations/Submission/"+lang+".tsv", "w", "utf-8")
	file.write(final_tsv)
	file.close()





