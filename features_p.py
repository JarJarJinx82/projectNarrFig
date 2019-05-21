#!/usr/bin/python3


def verb_proportion(text, tags):
	"""Anteil der Verben"""
	verb_count = 0
	total = len(tags)
	for word, tag in tags:
		if tag["pos"][0] == "V":
			verb_count += 1
	
	result = verb_count/ total
		
	return result 

def contains_neper_global(text, tags):
	"""Überprüft ob ein irgendein Personenname im Text vorkommt"""
	pass



if __name__ == "__main__":
	import pickle
	import inspect
	import sys

	with open("test.test", "rb") as testfile:
		tags = pickle.load(testfile)
		text = pickle.load(testfile)
	res = []
	functions = [obj for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj)]
	for f in functions:
		res.append((f.__name__, f(text, tags)))
	print(text)
	for elem in res:
		print(elem[0], elem[1])
